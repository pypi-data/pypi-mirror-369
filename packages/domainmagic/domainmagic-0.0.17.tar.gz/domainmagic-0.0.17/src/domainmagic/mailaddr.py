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

import typing as tp
import re
from domainmagic.validators import is_email


RE_BATV = re.compile(r'^(?:(?:ms)?prvs|btv)[0-9]?=')
RE_SRS = re.compile(r'^srs\d[+=]')
RE_EBL = re.compile('^(envelope-from|id|r|receiver)=')


class EmailAddressError(Exception):
    pass


try:
    import SRS
    HAVE_SRS = True

    class SRSDecode(SRS.Shortcut.Shortcut):
        def reverse(self, address: str) -> str:
            address = SRS.Shortcut.Shortcut.reverse(self, address)
            if is_srs(address):
                # if original address was srs1 address we need a second decoding run
                address = SRS.Shortcut.Shortcut.reverse(self, address)
            return address

        def parse(self, user: str, srshost: tp.Optional[str] = None) -> tp.Tuple[str, str]:
            # decode srs1= addresses
            user, m = self.srs1re.subn('', user, 1)
            if m:
                srshash, srshost, srsuser = user.split(SRS.SRSSEP, 2)[-3:]
                if srshash.find('.') >= 0:
                    srsuser = srshost + SRS.SRSSEP + srsuser
                    srshost = srshash
                return srshost, SRS.SRS0TAG + srsuser

            # decode srs0= addresses
            user, m = self.srs0re.subn('', user, 1)
            assert m, "Reverse address %s does not match %s." % (user, self.srs0re.pattern)
            fields = user.split(SRS.SRSSEP, 3)[-4:]
            assert len(fields) >= 4, "not enough data fields in address %s" % user
            myhash, timestamp, sendhost, senduser = fields
            if not sendhost and srshost:
                sendhost = srshost
            return sendhost, senduser
except ImportError:
    SRS = None
    HAVE_SRS = False
    SRSDecode = None


def is_srs(addr: str) -> bool:
    addr = addr.lower()
    if RE_SRS.match(addr):
        return True
    return False


def decode_srs(address: str) -> str:
    if HAVE_SRS and is_srs(address):
        srs = SRSDecode()
        return srs.reverse(address)
    else:
        return address


def email_normalise_low(address: str) -> str:
    """
    only convert address to lowercase
    :param address: email address to be normalised
    :return: normalised email address
    """
    if not address or not is_email(address):
        raise EmailAddressError(f'Not an email address: {address}')

    address = address.lower()
    return address


def _strip_tags(lhs: str, tagsep: str = '+') -> str:
    if len(lhs) > 1:  # strip "+" separated tags, but ignore "+" in first position.
        lhs0 = lhs[0]
        lhs1 = lhs[1:]
        if tagsep in lhs1:
            lhs = lhs0 + lhs1.split(tagsep)[0]
    return lhs


def _email_normalise_basic(address: str) -> tp.Tuple[str, str, tp.List[str]]:
    address = email_normalise_low(address)

    lhs, domain = split_mail(address, False)
    domainparts = domain.split('.')

    if 'googlemail' in domainparts:  # replace googlemail with gmail
        tld = '.'.join(domainparts[1:])
        domain = f'gmail.{tld}'
        domainparts = ['gmail', tld]

    lhs = _strip_tags(lhs)

    if 'gmail' in domainparts:  # discard periods in gmail
        lhs = lhs.replace('.', '')

    return lhs, domain, domainparts


def email_normalise_sh(address: str) -> str:
    """
    Email normalisation as proposed by SpamHaus
    see: https://docs.spamhaustech.com/datasets/docs/source/10-data-type-documentation/datasets/030-datasets.html?#email-email
    :param address: email address to be normalised
    :return: normalised email address
    """
    try:
        lhs, domain, domainparts = _email_normalise_basic(address)
    except EmailAddressError:
        return address

    return f'{lhs}@{domain}'


def email_normalise_ebl(address: str) -> str:
    """
    Email normalisation as proposed by EBL
    see: https://msbl.org/ebl-implementation.html
    :param address: email address to be normalised
    :return: normalised email address
    """
    try:
        lhs, domain, domainparts = _email_normalise_basic(address)
    except EmailAddressError:
        return address

    if 'yahoo' in domainparts or 'ymail' in domainparts:  # strip - tags from yahoo
        if '-' in lhs and lhs.index('-') != 1:  # do not strip e.g. x-asdf
            lhs = _strip_tags(lhs, '-')

    lhs = RE_EBL.sub('', lhs)  # strip mail log prefixes
    return f'{lhs}@{domain}'


def is_batv(address: str) -> bool:
    if RE_BATV.match(address):
        return True
    return False


def strip_batv(address: str) -> str:
    if is_batv(address):
        lhs, domain = split_mail(address, False)
        real_lhs = lhs.split('=', 2)[-1]
        address = f'{real_lhs}@{domain}'
    return address


def split_mail(address: str, strict: bool = False) -> tp.Tuple[str, str]:
    """
    Correctly splits an email address into local part and hostname part
    :param address: string with email address
    :param strict: bool strict check of email address
    :return: tuple of two strings: localpart and domain part
    """
    lhs = None
    dom = address
    if address is not None:
        if strict:
            valid = is_email(address)
        else:
            valid = '@' in address
        if valid:
            lhs, dom = address.rsplit('@', 1)
        dom = dom.lower()
    return lhs, dom


def domain_from_mail(address: str, strict: bool = False) -> str:
    """
    Returns domain/hostname from email address
    :param address: string with email address
    :param strict: bool strict check of email address
    :return: string with domain
    """
    return split_mail(address, strict)[1]


def extract_salesforce(address: str) -> str:
    """
    extracts the original sender address from a salesforce bounce address
    example: user=example.com__0-randomdata@randomdata.bnc.salesforce.com -> user@example.com
    :param address: string with email address
    :return: string with email address
    """
    lhs, domain = split_mail(address, False)
    if domain and lhs and domain.endswith('.bnc.salesforce.com') and '__' in lhs and '=' in lhs:
        addr = lhs.split('__')[0]
        if addr and '=' in addr:
            alhs, adom = addr.rsplit('=')
            address = f'{alhs}@{adom}'
    return address
