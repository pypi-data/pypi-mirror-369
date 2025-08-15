# -*- coding: UTF-8 -*-
#   Copyright Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#

from .tasker import TaskGroup, get_default_threadpool
from .tld import get_default_tldmagic
from .dnslookup import DNSLookup, DNSLookupResult
from .ip import ip_reversed, ip_convert_base10
from .validators import is_ip, is_hostname, is_email
from .mailaddr import strip_batv, decode_srs, domain_from_mail, extract_salesforce, EmailAddressError, \
    email_normalise_ebl, email_normalise_sh, email_normalise_low
from .util import get_logger
import logging
import re
from string import Template
import os
import hashlib
import time
import io
import base64
import typing as tp
import fnmatch
from collections import OrderedDict

try:
    from typing import OrderedDict as TpODict
except ImportError:  # python 3.6 and older
    from typing import MutableMapping
    TpODict = MutableMapping

filecache = {}


def add_trailing_dot(value: str) -> str:
    if not value.endswith('.'):
        return value + '.'
    else:
        return value


class RBLProviderBase:

    """Baseclass for all rbl providers"""

    def __init__(self, rbldomain: str, domainconfig: tp.Optional[tp.Dict] = None, timeout: float = 3, lifetime: float = 10, logprefix: str = '') -> None:
        self.replycodes = {}
        self.rbldomain = rbldomain
        self.logger = get_logger(f'{__name__}.{self.rbldomain}', logprefix)

        nameservers = None
        if domainconfig and 'ns' in domainconfig:
            nameservers = domainconfig['ns'].split(',')
        self.rbldns = DNSLookup(timeout=timeout, lifetime=lifetime, nameservers=nameservers, logprefix=logprefix)
        # use system default resolvers for a/ns lookups
        self.resolver = DNSLookup(timeout=timeout, lifetime=lifetime, logprefix=logprefix)
        if domainconfig and 'template' in domainconfig:
            self.descriptiontemplate = domainconfig['template']
        else:
            # noinspection PyTypeChecker
            self.descriptiontemplate = PROVIDERTEMPLATES.get(self.__class__, DEFAULTTEMPLATE)
        self.lifetime = lifetime
        self.filters = None
        self.failsafe = True

    def add_replycode(self, mask: int, identifier: str = None) -> None:
        """
        add a replycode/bitmask.
        identifier is any object which will be returned if a dns result matches this replycode
        if identifier is not passed, the lookup domain will be used
        """

        if identifier is None:
            identifier = self.rbldomain
        self.replycodes[mask] = identifier

    def add_filters(self, filters: tp.Iterable[str] = None) -> None:
        self.filters = filters

    @staticmethod
    def _check_fnmatch(dnsresult: str, code: str) -> bool:
        if '*' in code or '?' in code:
            return fnmatch.fnmatch(dnsresult, code)
        return False

    def _listed_identifiers(self, inp: str, transform: str, dnsresult: str) -> tp.List[tp.Tuple[str, str]]:
        listings = []
        for code, identifier in self.replycodes.items():
            if dnsresult == str(code) or dnsresult == f"127.0.0.{code}" or self._check_fnmatch(dnsresult, str(code)):
                listings.append((identifier, self.make_description(
                    input=inp,
                    dnsresult=dnsresult,
                    transform=transform,
                    identifier=identifier,
                    replycode=code)))
        return listings

    def make_description(self, **values) -> str:
        """create a human readable listing explanation"""
        template = Template(self.descriptiontemplate)
        values['rbldomain'] = self.rbldomain
        return template.safe_substitute(values)

    _rgx_input = re.compile('^[a-zA-Z0-9.-]{2,256}$')

    def accept_input(self, value: str) -> bool:
        return self._rgx_input.match(value) is not None

    def transform_input(self, value: str) -> tp.List[str]:
        """transform input, eg, look up records or make md5 hashes here or whatever is needed for your specific provider and return a list of transformed values"""
        return [value, ]

    def make_lookup(self, transform: str) -> str:
        """some bls require additional modifications, even after input transformation, eg. ips must be reversed...
        by default we just fix trailing dots
        """
        return add_trailing_dot(transform) + self.rbldomain

    def listed(self, inp, parallel: bool = False) -> tp.List[tp.Tuple[str, str]]:
        listings = []
        if not self.accept_input(inp):
            self.logger.debug(f'value not acceptable for {self.rbldomain}: {inp}')
            return listings
        try:
            transforms = self.transform_input(inp)
        except EmailAddressError as e:
            self.logger.debug(f'invalid input for {self.rbldomain}: {str(e)}')
            return listings

        if parallel:
            lookup_to_trans = {}
            for transform in transforms:
                lookup_to_trans[self.make_lookup(transform)] = transform

            self.logger.debug(f"lookup_to_trans={lookup_to_trans}")

            multidnsresult = self.rbldns.lookup_multi(lookup_to_trans.keys())

            for lookup, arecordlist in multidnsresult.items():
                if lookup not in lookup_to_trans:
                    self.logger.error(f"dns error: I asked for {lookup_to_trans.keys()} but got '{lookup}' ?!")
                    continue

                for ipresult in arecordlist:
                    try:
                        listings.extend(self._listed_identifiers(inp, lookup_to_trans[lookup], ipresult.content))
                    except Exception as e:
                        self.logger.error(
                            f'lookup error {inp} on {self.rbldomain} with {e.__class__.__name__} {str(e)}')
        else:
            loopstarttime = time.time()
            for transform in transforms:
                lookup = self.make_lookup(transform)
                arecordlist = self.rbldns.lookup(lookup.encode('utf-8', 'ignore'))
                for ipresult in arecordlist:
                    try:
                        listings.extend(self._listed_identifiers(inp, transform, ipresult.content))
                    except Exception as e:
                        self.logger.error(
                            f'lookup error {inp} on {self.rbldomain} with {e.__class__.__name__} {str(e)}')

                runtime = time.time() - loopstarttime
                if runtime > self.lifetime:
                    self.logger.debug(
                        f'rbl lookup for {inp} on {self.rbldomain} aborted due to timeout after {runtime}s')
                    break

        return listings

    def __str__(self) -> str:
        return "<%s d=%s codes=%s>" % (self.__class__.__name__, self.rbldomain, self.replycodes)

    def __repr__(self) -> str:
        return str(self)


class BitmaskedRBLProvider(RBLProviderBase):

    def _listed_identifiers(self, inp: str, transform: str, dnsresult: str) -> tp.List[tp.Tuple[str, str]]:
        """returns a list of identifiers matching the dns result"""
        listings = []
        octets = dnsresult.split('.')
        if self.failsafe and octets[0] != '127':  # only process expected standard rbl results
            self.logger.warning(f'failsafe catch: got invalid dns result {dnsresult} for input {inp}')
            return listings
        for mask, identifier in self.replycodes.items():
            if int(octets[-1]) & mask == mask:
                desc = self.make_description(
                    input=inp,
                    transform=transform,
                    dnsresult=dnsresult,
                    identifier=identifier,
                    replycode=mask)
                listings.append((identifier, desc),)
        return listings


class ReverseIPLookup(RBLProviderBase):

    """IP lookups require reversed question"""

    def make_lookup(self, transform: str) -> str:
        transform = transform.lower()
        if is_ip(transform):
            transform = ip_convert_base10(transform)
            transform = ip_reversed(transform)
        return add_trailing_dot(transform) + self.rbldomain


class StandardURIBLProvider(ReverseIPLookup, BitmaskedRBLProvider):

    """
    This is the most commonly used rbl provider (uribl, surbl)
     - domains are A record lookups example.com.rbldomain.com
     - results are bitmasked
     - ip lookups are reversed
    """
    pass


class BitmaskedIPOnlyProvider(StandardURIBLProvider):

    """
    ip only lookups
    lookups are reversed (inherited from StandardURIBLProvider)
    """

    def accept_input(self, value: str) -> bool:
        return is_ip(value)


class FixedResultIPOnlyProvider(ReverseIPLookup, RBLProviderBase):

    """
    ip only lookups, like zen
    lookups are reversed (inherited from StandardURIBLProvider)
    """

    def accept_input(self, value: str) -> bool:
        return is_ip(value)


def valid_host_names(lookupresult: tp.List[DNSLookupResult]) -> tp.List[str]:
    """
    return a list of valid host names from a  lookup result
    """
    validnames = set()
    for rec in lookupresult:
        content = rec.content
        content = content.rstrip('.')
        if is_hostname(content, check_valid_tld=True):
            validnames.add(content)
    validnames = list(validnames)
    return validnames


class FixedResultNSNameProvider(RBLProviderBase):
    """Nameserver Name Blacklists (nsname-static)"""

    def transform_input(self, value: str) -> tp.List[str]:
        ret = []
        try:
            nsrecords = self.resolver.lookup(value, 'NS')
            return valid_host_names(nsrecords)

        except Exception as e:
            self.logger.warning(f"Exception in getting ns names: {e.__class__.__name__}: {str(e)}")

        return ret

    def accept_input(self, value: str) -> bool:
        return is_hostname(value, check_valid_tld=True)


class BlackNSNameProvider(StandardURIBLProvider, FixedResultNSNameProvider):
    """Nameserver Name Blacklists (nsname-bitmask)"""
    pass


class FixedResultNSIPProvider(ReverseIPLookup):
    """Nameserver IP Blacklists (nsip-fixed)"""

    def transform_input(self, value: str) -> tp.List[str]:
        """transform input, eg, make md5 hashes here or whatever is needed for your specific provider"""
        ret = []
        try:
            nsnamerecords = self.resolver.lookup(value, 'NS')
            nsnames = valid_host_names(nsnamerecords)
            for nsname in nsnames:
                arecords = self.resolver.lookup(nsname, 'A')
                ips = [record.content for record in arecords]
                for ip in ips:
                    if not ip in ret:
                        ret.append(ip)
        except Exception as e:
            self.logger.warning(f"Exception in black ns ip lookup: {e.__class__.__name__}: {str(e)}")

        return ret

    def make_lookup(self, transform: str) -> str:
        result = ip_reversed(transform) + '.' + self.rbldomain
        return result

    def accept_input(self, value: str) -> bool:
        return is_hostname(value, check_valid_tld=True)


class BlackNSIPProvider(StandardURIBLProvider, FixedResultNSIPProvider):
    """Nameserver IP Blacklists (nsip-bitmask)"""
    pass


class FixedResultAProvider(ReverseIPLookup):
    """A record blacklists (a-fixed)"""

    def transform_input(self, value: str) -> tp.List[str]:
        try:
            arecords = self.resolver.lookup(value, 'A')
            ips = [record.content for record in arecords]
            return ips
        except Exception as e:
            self.logger.warning(f"Exception on a record lookup: {e.__class__.__name__}: {str(e)}")
        return []

    def accept_input(self, value: str) -> bool:
        return is_hostname(value, check_valid_tld=True)


class BlackAProvider(StandardURIBLProvider, FixedResultAProvider):
    """A record blacklists (a-bitmask)"""
    pass


class SOAEmailProvider(StandardURIBLProvider):

    """Black SOA Email"""

    def transform_input(self, value: str) -> tp.List[str]:
        try:
            soaemails = []
            soarecords = self.resolver.lookup(value, 'SOA')
            if len(soarecords) == 0:
                domain = get_default_tldmagic().get_domain(value)
                soarecords = self.resolver.lookup(domain, 'SOA')

            for rec in soarecords:
                parts = rec.content.split()
                if len(parts) != 7:
                    continue
                email = parts[1].rstrip('.')
                soaemails.append(email)

            return soaemails  # TODO: is this correct or should we return hashes of the email addresses? see #14
        except Exception as e:
            self.logger.warning(f"{e.__class__.__name__} on SOA record lookup: {str(e)}")
        return []


class EmailBLSimpleProvider(StandardURIBLProvider):
    """
    Simple EmailBL query provider.
    Returns one hash of normalised email address
    Hash and normalisation is determined by passed filters, defaults to md5 and lowercase only
    """

    def _get_domainlist(self) -> tp.Optional[tp.List[str]]:
        domainlist = None
        if not self.filters:
            return domainlist
        for item in self.filters:
            if item.startswith('file='):
                path = item.split('=')[-1]
                if os.path.exists(path):
                    now = time.time()
                    try:
                        values, ts = filecache[path]
                        if ts < now-600:  # only read file every n seconds
                            values = None
                    except KeyError:
                        values = None
                    if values is not None:
                        domainlist = values
                    else:
                        with open(path) as f:
                            domainlist = f.readlines()
                            # remove trailing spaces & newlines
                            domainlist = [d.strip() for d in domainlist if d.strip()]
                            filecache[path] = (domainlist, now)
        return domainlist

    def accept_input(self, value: str) -> bool:
        if not is_email(value):
            return False
        domainlist = self._get_domainlist()
        if domainlist is None:  # no domainlist: accept every mail address
            return True
        domain = domain_from_mail(value)
        return domain in domainlist

    def _get_format(self) -> tp.Tuple[str, tp.Callable, tp.Callable, tp.Callable]:
        normalisers = {
            'low': email_normalise_low,
            'sh': email_normalise_sh,
            'ebl': email_normalise_ebl,
        }

        extractors = {
            'salesforce': extract_salesforce
        }

        encoders = {
            'hex': lambda x: x.hexdigest(),
            'b64': lambda x: base64.b64encode(x.digest()).decode().rstrip('='),
            'b32': lambda x: base64.b32encode(x.digest()).decode().rstrip('='),
        }

        hashtype = 'md5'
        normaliser = email_normalise_low
        def extractor(x): return x
        encoder = encoders['hex']
        if self.filters is None:
            pass
        else:
            for fltr in self.filters:
                fltr.lower()
                if fltr in hashlib.algorithms_available:
                    hashtype = fltr
                elif fltr in normalisers:
                    normaliser = normalisers[fltr]
                elif fltr in list(encoders.keys()):
                    encoder = encoders[fltr]
                elif fltr in list(extractors.keys()):
                    extractor = extractors[fltr]
                elif fltr.startswith('file='):
                    pass
                else:
                    self.logger.warning(f'invalid filter definition: {fltr}')

        return hashtype, extractor, normaliser, encoder

    def transform_input(self, value: str) -> tp.List[str]:
        hashtype, extractor, normaliser, encoder = self._get_format()
        value = extractor(value)
        value = normaliser(value)
        hasher = hashlib.new(hashtype, value.encode())
        return [encoder(hasher)]


class EmailBLMultiProvider(EmailBLSimpleProvider):
    """
    Complex EmailBL query provider
    Returns one or multiple hashes of various normalisations of email address
    Hash: anyone supported by hashlib, defaults to md5
    Normalisations:
        - lowercase only
        - strip batv tags + lowercase
        - decode srs + lowercase
        - according to normaliser definition (low/sh/ebl, including stripped batv and decoded srs)
    """

    def transform_input(self, value: str) -> tp.List[str]:
        value = value.lower()
        values = {value}
        batvvalue = strip_batv(value)
        values.add(batvvalue.lower())
        srsvalue = decode_srs(value)
        values.add(srsvalue)

        hashtype, extractor, normaliser, encoder = self._get_format()
        for value in values:
            value = extractor(value)
            values.add(value)
        for value in values:
            value = normaliser(value)
            values.add(value)

        hashes = []
        for v in values:
            hasher = hashlib.new(hashtype, v.encode())
            hashes.append(encoder(hasher))

        return hashes


class FixedResultDomainProvider(RBLProviderBase):

    """uribl lookups with fixed return codes and ip lookups disabled, like the spamhaus DBL"""

    def accept_input(self, value: str) -> bool:
        if not super(FixedResultDomainProvider, self).accept_input(value):
            return False

        if is_ip(value):  # dbl is the only known fixed result domain provider and does not allow ip lookups, so we filter this here
            return False

        return True


DEFAULTTEMPLATE = "${input} is listed on ${rbldomain} (${identifier})"
PROVIDERTEMPLATES = {
    BlackNSNameProvider: "${input}'s NS name ${transform} is listed on ${rbldomain} (${identifier})",
    BlackNSIPProvider: "${input}'s NSIP ${transform} is listed on ${rbldomain} (${identifier})",
    BlackAProvider: "${input}'s A record ${transform} is listed on ${rbldomain} (${identifier})",
    SOAEmailProvider: "${input}'s SOA email ${transform} is listed on ${rbldomain} (${identifier})",
    FixedResultAProvider: "${input}'s A record ${transform} is listed on ${rbldomain} (${identifier})",
    FixedResultNSNameProvider: "${input}'s NS name ${transform} is listed on ${rbldomain} (${identifier})",
    FixedResultNSIPProvider: "${input}'s NSIP ${transform} is listed on ${rbldomain} (${identifier})",
}


class RBLLookup:

    def __init__(self, timeout: float = 3, lifetime: float = 10, logprefix: str = ''):
        self.logger = get_logger(__name__, logprefix)
        self.providers = []
        self.timeout = timeout
        self.lifetime = lifetime

        self.providermap = {
            'uri-bitmask': StandardURIBLProvider,
            'ip-bitmask': BitmaskedIPOnlyProvider,
            'ip-fixed': FixedResultIPOnlyProvider,
            'domain-fixed': FixedResultDomainProvider,
            'uri-fixed': FixedResultDomainProvider,  # alias for domain-fixed
            'nsip-bitmask': BlackNSIPProvider,
            'nsip-fixed': FixedResultNSIPProvider,
            'nsname-bitmask': BlackNSNameProvider,
            'nsname-fixed': FixedResultNSNameProvider,
            'a-bitmask': BlackAProvider,
            'a-fixed': FixedResultAProvider,
            'email-bitmask': EmailBLSimpleProvider,
            'multi-email-bitmask': EmailBLMultiProvider,
            'soaemail-bitmask': SOAEmailProvider,
        }

    def from_config(self, filepath: tp.Optional[str] = None) -> None:
        if not filepath:
            return

        self.logger.debug(f'loading rbl lookups from file {filepath}')
        if not os.path.exists(filepath):
            self.logger.error(f"File not found:{filepath}")
            return

        providers = []

        with io.open(filepath) as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue

            parts = line.split(None, 2)
            if len(parts) != 3:
                self.logger.error(f"invalid config line: {line}")
                continue

            providertype, searchdom, resultconfig = parts
            if providertype not in self.providermap:
                self.logger.error(f"unknown provider type {providertype} for {searchdom}")
                continue

            domainconfig = {}
            if ':' in searchdom:
                domainconf = searchdom.split(':')
                searchdomain = domainconf[0]
                if len(domainconf) > 1:
                    domainconfig = {k: v for k, v in [x.split('=') for x in domainconf[1:]]}
            else:
                searchdomain = searchdom

            providerclass = self.providermap[providertype]
            providerinstance = providerclass(searchdomain, domainconfig=domainconfig,
                                             timeout=self.timeout, lifetime=self.lifetime, logprefix=self.logger.prefix)

            # set bitmasks and filters
            for res in resultconfig.split():
                filters = None
                if ':' in res:
                    fields = res.split(':')
                    try:
                        code = int(fields[0])
                    except (ValueError, TypeError):
                        # fixed value
                        code = fields[0]
                    identifier = fields[1]
                    if len(fields) > 2:
                        filters = fields[2:]
                else:
                    identifier = res
                    code = 2

                providerinstance.add_replycode(code, identifier)
                providerinstance.add_filters(filters)
            providers.append(providerinstance)
        self.providers = providers
        self.logger.debug(f"Providerlist from configfile: {providers}")

    def listings(self, checkvalue: str, timeout: float = 10, parallel: bool = False, abort_on_hit: bool = False, skip_rbldomains: tp.Iterable[str] = ()) -> TpODict[str, str]:
        """
        return a dict identifier:humanreadable for each listing
        warning: parallel is very experimental and has bugs - do not use atm
        """
        listed = OrderedDict()

        if parallel:
            tg = TaskGroup()
            for provider in self.providers:
                if provider.rbldomain in skip_rbldomains:
                    self.logger.debug(f'{provider.rbldomain} lookups skipped')
                    continue
                tg.add_task(provider.listed, (checkvalue,), comment=provider.rbldomain)
            threadpool = get_default_threadpool()
            threadpool.add_task(tg)
            tg.join(timeout)

            listresults = {}
            for task in tg.tasks:
                if task.done:
                    for identifier, humanreadable in task.result:
                        if identifier not in listed:
                            listresults[identifier] = (humanreadable, task.comment)
                        else:
                            self.logger.warning(f'duplicate identifier {identifier} hit will be lost: {humanreadable}')
            threadpool.stayalive = False
            for provider in self.providers:  # sort results by order from config
                for item in listresults:
                    if listresults[item][1] == provider.rbldomain:
                        listed[item] = listresults[item][0]
                        break
        else:
            starttime = time.time()
            for provider in self.providers:
                if provider.rbldomain in skip_rbldomains:
                    self.logger.debug(f'{provider.rbldomain} lookups skipped')
                    continue
                loopstarttime = time.time()
                runtime = loopstarttime - starttime
                if 0 < timeout < runtime:
                    self.logger.info(f'{provider.rbldomain} lookups aborted after {runtime:.2f}s due to timeout')
                    break

                for identifier, humanreadable in provider.listed(checkvalue):
                    if identifier not in listed:
                        listed[identifier] = humanreadable
                    else:
                        self.logger.warning(f'duplicate identifier {identifier} hit will be lost: {humanreadable}')
                    if abort_on_hit:
                        return listed.copy()

                self.logger.debug(f'{provider.rbldomain} completed in {time.time()-loopstarttime:.2f}s')

        return listed.copy()

    def listings_recursive(self, checkvalue: str, *args, **kwargs) -> TpODict[str, str]:

        if is_hostname(checkvalue, check_valid_tld=True):
            listings = {}
            tldcount = get_default_tldmagic().get_tld_count(checkvalue)
            parts = checkvalue.split('.')
            subrange = range(tldcount+1, len(parts)+1)
            for subindex in subrange:
                subdomain = '.'.join(parts[-subindex:])
                l = self.listings(subdomain, *args, **kwargs)
                listings.update(l)
        else:
            listings = self.listings(checkvalue, *args, **kwargs)
        return listings


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("usage: rbl </path/to/rbl.conf> <domain> [-debug]")
        sys.exit(1)

    rbl = RBLLookup()
    rbl.from_config(sys.argv[1])

    if '-debug' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)

    query = sys.argv[2]

    start = time.time()
    ans = rbl.listings(query)
    end = time.time()
    diff = end - start
    for ident, expl in ans.items():
        print(f"identifier '{ident}' because: {expl}")

    print("")
    print("execution time: %.4f" % diff)
    sys.exit(0)
