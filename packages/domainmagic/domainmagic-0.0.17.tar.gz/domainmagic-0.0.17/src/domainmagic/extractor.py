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
import re
import os
import time
import logging
from .tld import get_IANA_TLD_list
from .validators import REGEX_IPV4, REGEX_IPV6, is_hostname, is_ip, is_url, HEXREGEX_IPV4, is_cidr
from .util import get_logger
from .ip import ip_convert_base10
import traceback
import io
import urllib.parse
from html import unescape as html_unescape
import typing as tp
import ipaddress
import base64

if hasattr(re, 'Pattern'):
    repattern = re.Pattern
elif hasattr(re, '_pattern_type'):  # python3.6
    # noinspection PyProtectedMember
    repattern = re._pattern_type
else:  # generic
    repattern = re.compile('').__class__


EMAIL_HACKS = {
    '@': ['(at)', ' (at) ', ' AT ', '[at]', ' @ '],
    '.': ['(dot)', ' (dot) ', ' DOT ', '[dot]', ' . '],
}

# extraction hacks (use as bitmask for `use_hacks` parameter)
EX_HACKS_PROCURL = 0x01  # Search & extract URLs in URL parameters
EX_HACKS_IDNA = 0x02  # convert characters using "Internationalizing Domain Names in Applications"
EX_HACKS_LAZYHOSTNAME = 0x04  # Use lazy hostname regex in is_hostname allowing "_"


def build_search_re(tldlist=None):
    if tldlist is None:
        tldlist = get_IANA_TLD_list()

    # lookbehind to check for start of url
    # start with
    # - start of string
    # - whitespace
    # - " for href
    # - ' for borked href
    # - = borked href without " or '
    # - > for links in tags
    # - () after opening or closing parentheses (seen in chinese spam)
    # - * seen in spam
    # - - seen in spam (careful, legit character in hostname)
    # - [ for links in square brackets (seen in spam)
    # - allow ":" in front of link if not followed by //, for example "confuse:www.domain.invalid"
    reg = r"(?:(?<=^)|(?<="
    reg += r"(?:\s|[\"'=\<\>\(\)\*\[]|:(?!\/\/))"
    reg += r"))"

    # url starts here
    reg += r"(?:"
    reg += r"(?:https?://|ftp://)"  # protocol
    reg += r"(?:[a-z0-9!%_$.+=\-]+(?::[a-z0-9!%_$.+=\-]+)?@)?"  # username/pw
    reg += r")?"

    # domain
    reg += r"(?:"  # domain types

    # standard domain
    allowed_hostname_chars = r"-a-z0-9_"
    reg += r"[a-z0-9_]"  # first char can't be a hyphen
    reg += r"[" + allowed_hostname_chars + \
        r"]*"  # there are domains with only one character, like 'x.org'
    reg += r"(?:\.[" + allowed_hostname_chars + \
        r"]+)*"  # more hostname parts separated by dot
    reg += r"\."  # dot between hostname and tld
    reg += r"(?:"  # tldgroup
    reg += r"|".join([x.replace('.', r'\.') for x in tldlist])
    reg += r")\.?"  # standard domain can end with a dot

    # dotquad
    reg += rf"|{REGEX_IPV4}"
    reg += rf"|{HEXREGEX_IPV4}"

    # ip6
    reg += rf"|\[{REGEX_IPV6}\]"

    reg += r")"  # end of domain types

    # optional port
    reg += r"(?:\:\d{1,5})?"

    # after the domain, there must be a path sep or quotes space or ?
    # or > (for borked href without " or ') end,
    # or ] (for domain-only uri in square brackets')
    # or < (for uri enclosed in html tag)
    # or ) (for uri enclosed in parenthesis)
    # check with lookahead
    reg += r"""(?=[<>\"'/?\]\[)]|\s|$)"""

    # path
    allowed_path_chars = r"-a-z0-9._/%#\[\]~*!"
    reg += r"(?:\/[" + allowed_path_chars + r"]+)*"

    # request params
    allowed_param_chars = r"-a-z0-9;._/\![\]?#+%&=@*,:!"
    reg += r"(?:\/?)"  # end domain with optional  slash
    reg += r"(?:\?[" + allowed_param_chars + \
        r"]*)?"  # params must follow after a question mark

    # print(f"RE: {reg}")
    return re.compile(reg, re.IGNORECASE)


def build_email_re(tldlist=None):
    if tldlist is None:
        tldlist = get_IANA_TLD_list()

    reg = r"(?=.{0,64}\@)"                         # limit userpart to 64 chars
    reg += r"(?<![a-z0-9!#$%&'*+\/=?^_`{|}~-])"     # start boundary
    reg += r"("                                             # capture email
    reg += r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+"         # no dot in beginning
    reg += r"(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*"  # no consecutive dots, no ending dot
    reg += r"\@"
    reg += r"[-a-z0-9._]+\."  # hostname
    reg += r"(?:"  # tldgroup
    reg += r"|".join([x.replace('.', r'\.') for x in tldlist])
    reg += r")"
    reg += r")(?!(?:[a-z0-9-]|\.[a-z0-9]))"          # make sure domain ends here
    return re.compile(reg, re.IGNORECASE)


def domain_from_uri(uri: str) -> str:
    """backwards compatibilty name"""
    return fqdn_from_uri(uri)


def fqdn_from_uri(uri: str) -> str:
    """extract the domain(fqdn) from uri"""
    if '://' not in uri:
        uri = "http://" + uri
    fqdn = urllib.parse.urlparse(uri.lower()).netloc

    # remove user/pass:
    if '@' in fqdn:
        fqdn = fqdn.rsplit('@')[-1]

    # remove port
    portmatch = re.search(r':\d{1,5}$', fqdn)
    if portmatch is not None:
        fqdn = fqdn[:portmatch.span()[0]]

    # remove square brackets from ipv6
    fqdn = fqdn.strip('[]')

    return fqdn


def redirect_from_google(uri: str) -> str:
    """backwards compatibilty name"""
    return redirect_from_url(uri)


_re_amp = re.compile('^amp/(.*)')
_re_httpslash = re.compile('^(https?):/([^/].*)')  # find uris with single slash after http/https


def redirect_from_url(uri: str, silent: bool = True) -> str:
    """extract target domain from cloaking redirection services"""
    try:
        parsed = urllib.parse.urlparse(html_unescape(uri))
        if ('google.' in parsed.netloc and parsed.path == '/url') or \
            ('translate.google' in parsed.netloc and parsed.path == '/translate') or \
            (parsed.netloc.endswith(('safelinks.protection.outlook.com', '.urlsand.com')) and parsed.path == '/') or \
                ('yandex.' in parsed.netloc and parsed.path == '/redirect') or \
                (parsed.netloc.endswith('.yusercontent.com') and parsed.path == '/mail'):
            values = urllib.parse.parse_qs(parsed.query)
            for key in ['url', 'q', 'u']:
                uris = [v for v in [_re_amp.sub(r'https://\g<1>', u) for u in values.get(key, [])] if is_url(v)]
                if len(uris) > 0:
                    uri = uris[0]  # we expect exactly one redirect
                    if uri:
                        break
        elif parsed.netloc == 'urldefense.com' and parsed.path.startswith('/v3/__'):
            # https://urldefense.com/v3/__http:/www.example.com/foo/bar__;!!somehashdata$
            items = parsed.path.split('__', 1)[-1]
            uri = items.rsplit('__', 1)[0]
            uri = _re_httpslash.sub(r'\g<1>://\g<2>', uri)  # replace single slash by double slash
        elif parsed.netloc in ['bing.com', 'www.bing.com'] and parsed.path == '/ck/a':
            qs = urllib.parse.parse_qs(parsed.query)
            if 'psq' in qs and qs['psq']:
                value = qs['psq'][0] # value may be non-uri search term
                if is_url(value) or is_hostname(value):
                    uri = value
            if not uri and 'u' in qs and qs['u'][0].startswith('a1'):
                try:
                    value = base64.b64decode(qs['u'][0][2:]).decode()
                    if is_url(value) or is_hostname(value):
                        uri = value
                except Exception:
                    pass
        elif parsed.netloc.endswith('.awstrack.me') and parsed.path.startswith('/L0/'):
            extr = parsed.path[4:].split('/')[0]
            unquoted = urllib.parse.unquote(extr)
            if is_url(unquoted):
                uri = unquoted
        elif parsed.netloc.endswith('.doubleclick.net'):
            qs = urllib.parse.parse_qs(parsed.query)
            adurl = qs.get('adurl')
            if adurl and adurl[0].startswith('///'):
                uri = 'https:' + adurl[0][1:]
        elif parsed.scheme in ['viber', 'whatsapp'] and parsed.query.startswith('text='):
            uri = parsed.query[5:]
    except Exception:
        if not silent:
            raise
    return uri


def direct_param_url(uri: str, silent: bool = True, use_hacks: int = 0) -> str:
    """check for unencoded urls in parameter list"""

    # search keys in parameter list
    skeys = ["https://", "http://"]

    try:
        parsed = urllib.parse.urlparse(html_unescape(uri))
        values = urllib.parse.parse_qs(parsed.query)
        if (use_hacks == EX_HACKS_PROCURL) and parsed.query and not any(k in parsed.query for k in skeys):
            return uri

        for pname, plist in values.items():
            for key in ["https://", "http://"]:
                for pval in plist:
                    if key in pval:
                        # return first hit
                        return pval[pval.find(key):]
    except Exception:
        if not silent:
            raise
    return uri


def normalise_blogspot_fqdn(fqdn: str) -> str:
    sp = fqdn.split('.')
    if 'blogspot' in sp:
        idx = sp.index('blogspot')
        dom = sp[:idx+1]
        dom.append('com')
        fqdn = '.'.join(dom)
    return fqdn


def normalise_blogspot_uri(uri: str) -> str:
    try:
        parsed = urllib.parse.urlparse(uri)
        if '.blogspot.' in parsed.netloc:
            fqdn = normalise_blogspot_fqdn(parsed.netloc)
            parsed = parsed._replace(netloc=fqdn)
            parsed = parsed._replace(scheme='https')
            uri = parsed.geturl()
    except Exception:
        pass
    return uri


class URIExtractor:

    """Extract URIs"""

    def __init__(self, tldlist: list = None, logprefix='') -> None:
        self.tldlist = tldlist
        self.lastreload = time.time()
        self.lastreloademail = time.time()
        self.logger = get_logger(__name__, logprefix)
        self.searchre = build_search_re(self.tldlist)
        self.emailre = build_email_re(self.tldlist)
        self.skiplist = set()
        self.maxregexage = 86400  # rebuild search regex once a day so we get new tlds

    def set_tld_list(self, tldlist: list) -> None:
        """override the tldlist and rebuild the search regex"""
        self.tldlist = tldlist
        self.searchre = build_search_re(tldlist)
        self.emailre = build_email_re(tldlist)

    def load_skiplist(self, filename: str) -> None:
        entries = self._load_single_file(filename)
        skiplist = self.gen_complex_skiplist(entries)
        self.skiplist = skiplist

    @staticmethod
    def gen_complex_skiplist(entries: tp.Set[str]) -> tp.Set:
        skiplist = set()
        for entry in entries:
            if entry.startswith('/') and entry.endswith('/'):
                entry = entry.strip('/')
                skiplist.add(re.compile(entry))
            elif is_cidr(entry):
                skiplist.add(ipaddress.ip_network(entry, False))
            else:
                skiplist.add(entry)
        return skiplist

    def _load_single_file(self, filename: str) -> tp.Set[str]:
        """return lowercased set of unique entries"""
        if not os.path.exists(filename):
            self.logger.error(f"File {filename} not found - skipping")
            return set()
        with io.open(filename, 'r') as f:
            content = f.read().lower()
        entries = content.split()
        del content
        return set(entries)

    def _uri_filter(self, uri: str, use_hacks: int = 0, skip_unrouted_ips: bool = False) -> tp.Tuple[bool, str, str]:
        skip = False
        newuri = None
        try:
            domain = fqdn_from_uri(uri.lower())
            domain = ip_convert_base10(domain)
        except Exception:
            skip = True
            domain = None

        # work around extractor bugs - these could probably also be fixed in the search regex
        # but for now it's easier to just throw them out
        if not skip and domain and '..' in domain:  # two dots in domain
            skip = True

        if not skip and not (is_hostname(domain, lazyhostname=(use_hacks & EX_HACKS_LAZYHOSTNAME)) or is_ip(domain)):
            skip = True

        if not skip and (use_hacks & EX_HACKS_PROCURL):
            newuri = redirect_from_url(uri)
            newuri = normalise_blogspot_uri(newuri)
            newuri = direct_param_url(newuri, use_hacks=use_hacks)

        ipdomain = None
        if not skip and is_ip(domain):
            try:
                ipdomain = ipaddress.ip_address(domain)
                if skip_unrouted_ips:
                    skip = not ipdomain.is_global
            except ValueError:
                self.logger.warning(f'not a valid IP address: {domain}')

        if not skip:
            for skipentry in self.skiplist:
                if isinstance(skipentry, str) and (domain == skipentry or domain == f"{skipentry}." or domain.endswith(f'.{skipentry}') or domain.endswith(f'.{skipentry}.')):
                    skip = True
                elif isinstance(skipentry, repattern) and skipentry.search(domain):
                    skip = True
                elif ipdomain is not None and isinstance(skipentry, (ipaddress.IPv4Network, ipaddress.IPv6Network)) and ipdomain in skipentry:
                    skip = True
                if skip:
                    break

        # axb: trailing dots are probably not part of the uri
        if uri.endswith('.'):
            uri = uri[:-1]
        # also check new uri to prevent a loop with the same uri
        if newuri and newuri.endswith('.'):
            newuri = newuri[:-1]

        return skip, uri, newuri

    def _idna_convert(self, plaintext: str) -> str:
        """
        convert single characters to their idna equivalent. converts unicode lookalikes to their ascii counterpart.
        :param plaintext: text to convert
        :return: converted text
        """
        output = ''
        for c in plaintext:
            if c in {'.'}:  # . cannot be idna converted. other characters may be affected too...
                output += c
            else:
                try:
                    b = c.encode('idna')
                except UnicodeError as e:
                    # self.logger.debug(f'failed to convert {c} to idna due to {str(e)}')
                    pass
                else:
                    try:
                        output += b.decode()
                    except UnicodeDecodeError as e:
                        self.logger.warning(f'failed to convert idna of {c} to unicode due to {str(e)}')
        return output

    def extracturis(self, plaintext: str, use_hacks: int = 0, skip_unrouted_ips: bool = False) -> tp.List[str]:
        """
        Find URIs in a text
        :param plaintext: text to search for URIs
        :param use_hacks: set the level of hacks to apply. 0=no hacks, 1=find uris within uris
        :param skip_unrouted_ips: ignore URIs where the host part is a non routed IP address (e.g. 127.0.0.1)
        :return: list of URIs
        """

        # convert use_hacks to integer level
        if not isinstance(use_hacks, int):
            use_hacks = EX_HACKS_PROCURL if use_hacks else 0

        if use_hacks & EX_HACKS_IDNA:
            plaintext = self._idna_convert(plaintext)

        if self.tldlist is None and time.time() - self.lastreload > self.maxregexage:
            self.lastreload = time.time()
            self.logger.debug("Rebuilding search regex with latest TLDs")
            try:
                self.searchre = build_search_re()
            except Exception:
                self.logger.error(f'Rebuilding search re failed: {traceback.format_exc()}')

        uris = []
        uris.extend(re.findall(self.searchre, plaintext))

        finaluris = []
        # check skiplist and apply recursive extraction hacks
        for newuri in uris:
            counter = 0
            while newuri is not None and counter < 100:
                # use a counter to be sure we never end up
                # in an infinite loop
                counter += 1

                skip, uri, newuri = self._uri_filter(newuri, use_hacks, skip_unrouted_ips)
                skipnew = skip

                # skip partial uris and uri fragments due to parsing/extraction errors
                for finaluri in finaluris:
                    if uri in finaluri:
                        skip = True

                if not skip:
                    finaluris.append(uri)

                if newuri != uri and newuri is not None and not skipnew:
                    finaluris.append(newuri)

                if skipnew or newuri == uri:
                    # don't continue if skipenew is True
                    newuri = None

        # remove left-alone trailing square bracket
        cleaneduris = []
        for furi in finaluris:
            if furi.endswith("]"):
                countleft = furi.count("[")
                countright = furi.count("]")
                if countleft < countright and len(furi) > 1:
                    cleaneduris.append(furi[:-1])
                    continue
            cleaneduris.append(furi)
        return sorted(set(cleaneduris))

    def extractemails(self, plaintext: str, use_hacks: int = 0, skip_unrouted_ips: bool = False) -> tp.List[str]:
        """
        Find Email addresses in a text
        :param plaintext: text to search for email addresses
        :param use_hacks: set the level of hacks to apply. 0=no hacks, 1=minor fixups (e.g. ..->.), 2=replace at and dot strings with @ and .
        :param skip_unrouted_ips: currently unused, for compatibility with extracturis()
        :return: list of email addresses
        """
        if time.time() - self.lastreloademail > self.maxregexage:
            self.lastreloademail = time.time()
            self.logger.debug("Rebuilding search regex with latest TLDs")
            try:
                self.emailre = build_email_re()
            except Exception:
                self.logger.error(f'Rebuilding email search re failed: {traceback.format_exc()}')

        # convert use_hacks to integer level
        if not isinstance(use_hacks, int):
            use_hacks = 1 if use_hacks else 0

        if use_hacks == 1:
            plaintext = plaintext.replace('..', '.')
            plaintext = plaintext.replace('_', '-')

        if use_hacks > 1:
            plaintext = self._idna_convert(plaintext)
            for key in EMAIL_HACKS:
                for value in EMAIL_HACKS[key]:
                    plaintext = plaintext.replace(value, key)

        emails = []
        emails.extend(re.findall(self.emailre, plaintext))
        return sorted(set(emails))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    extractor = URIExtractor()
    # logging.info(extractor.extracturis("hello http://unittests.fuglu.org/?doener lol
    # yolo.com . blubb.com."))

    # logging.info(extractor.extractemails("blah a@b.com someguy@gmail.com"))

    txt = """
    hello 
    http://bla.com 
    please click on <a href="www.co.uk">slashdot.org/?a=c&f=m</a> 
    or on <a href=www.withoutquotes.co.uk>slashdot.withoutquotes.org/?a=c&f=m</a>   
    www.skipme.com www.skipmenot.com/ x.co/4to2S http://allinsurancematters.net/lurchwont/ muahahaha x.org
    dash-domain.org http://dash2-domain2.org:8080 <a href="dash3-domain3.org/with/path">
    """
    logging.info(extractor.extracturis(txt))
