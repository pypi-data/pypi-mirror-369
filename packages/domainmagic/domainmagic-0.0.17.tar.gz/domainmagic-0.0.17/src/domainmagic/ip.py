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

"""ip tools"""

from .fileupdate import updatefile
from .validators import is_ipv4
import stat
import ipaddress
import re

try:
    import geoip2.database
    PYGEOIP_AVAILABLE = True
except ImportError:
    PYGEOIP_AVAILABLE = False


GEOIP_FILE = '/tmp/GeoLite2-Country.mmdb'
GEOIP_URL = 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'


def ip6_expand(ip: str) -> str:
    """
    remove :: shortcuts from ip adress - the returned address has 8 parts
    deprecated, better use ipaddress directly
    """
    if '.' in ip:
        raise ValueError()

    addr = ipaddress.ip_address(ip)
    return addr.exploded


def ip_reversed(ip: str) -> str:
    """Return the reversed ip address representation for dns lookups"""
    addr = ipaddress.ip_address(ip)
    revptr = addr.reverse_pointer
    items = revptr.split('.')
    return '.'.join(items[:-2])


# deprecated
def convert_hex_ip(ip: str) -> str:
    return ip_convert_base10(ip)


_re_hexip = re.compile('^0x[0-9a-f]{1,2}$')
_re_octip = re.compile('^0o?[0-7]{1,3}$')


def ip_convert_base10(ip: str) -> str:
    if is_ipv4(ip):
        ipbytes = ip.split('.')
        intvals = []
        try:
            for ipbyte in ipbytes:
                if _re_hexip.match(ipbyte):
                    intvals.append(str(int(ipbyte, 16)))
                elif _re_octip.match(ipbyte):
                    intvals.append(str(int(ipbyte, 8)))
                elif ipbyte == '0':
                    intvals.append(ipbyte)
                else:
                    ipbyte = str(int(ipbyte.lstrip('0'), 0))  # strip leading zeroes, fixes strict check in py3.10
                    intvals.append(ipbyte)
            ip = '.'.join(intvals)
        except ValueError:
            raise ValueError(f'invalid IP address: {ip}')
    return ip


@updatefile(GEOIP_FILE, GEOIP_URL, refresh_time=24*3600, minimum_size=1000, unpack=True,
            filepermission=stat.S_IWUSR | stat.S_IRUSR | stat.S_IWGRP | stat.S_IRGRP | stat.S_IROTH)
def geoip_country_code_by_addr(ip: str) -> str:
    assert PYGEOIP_AVAILABLE, "geoip2 is not installed"
    gi = geoip2.database.Reader(GEOIP_FILE)
    data = gi.country(ip)
    retval = data.country.iso_code
    if retval is None:  # some ips are not assigned to a country, only to a continent (usually EU)
        retval = data.continent.code
    return retval
