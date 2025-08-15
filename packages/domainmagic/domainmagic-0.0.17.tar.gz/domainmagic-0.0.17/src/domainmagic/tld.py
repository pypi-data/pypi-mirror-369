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

from .util import tld_tree_update, tld_list_to_tree, tld_tree_path, get_logger, tp_tree
from .fileupdate import updatefile
import io
import re
import stat
import typing as tp


@updatefile('/tmp/tlds-alpha-by-domain.txt', 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt',
            minimum_size=1000, refresh_time=86400, force_recent=True,
            filepermission=stat.S_IWUSR | stat.S_IRUSR | stat.S_IWGRP | stat.S_IRGRP | stat.S_IROTH)
def get_IANA_TLD_list() -> tp.List[str]:
    tlds = []
    try:
        with io.open('/tmp/tlds-alpha-by-domain.txt') as fp:
            content = fp.readlines()
    except IOError:
        logger = get_logger(__name__)
        logger.error("Error trying to open file /tmp/tlds-alpha-by-domain.txt")
        content = []

    for line in content:
        if line.strip() == '' or line.startswith('#'):
            continue
        tlds.extend(line.lower().split())
    return sorted(tlds)


default_tldmagic = None


def get_default_tldmagic():
    global default_tldmagic
    if default_tldmagic is None:
        default_tldmagic = TLDMagic()
    return default_tldmagic


_re_label = re.compile(r'^[a-z0-9\-.]{2,64}$')


def load_tld_file(filename: str) -> tp.List[str]:
    retval = []
    with io.open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('#') or line.strip() == '':
            continue
        tlds = line.split()
        for tld in tlds:
            if tld.startswith('.'):
                tld = tld[1:]
            tld = tld.lower()
            if _re_label.match(tld):
                if tld not in retval:
                    retval.append(tld)
    return retval


class TLDMagic:

    def __init__(self, initialtldlist: tp.Iterable[str] = ()) -> None:
        self.tldtree: tp_tree = {}  # store
        if not initialtldlist:
            self._add_iana_tlds()
        else:
            for tld in initialtldlist:
                self.add_tld(tld)

    def _add_iana_tlds(self) -> None:
        for tld in get_IANA_TLD_list():
            self.add_tld(tld)

    def get_tld(self, fqdn: str) -> tp.Optional[str]:
        """get the tld from domain, returning the largest possible xTLD"""
        fqdn = fqdn.lower()
        parts = fqdn.split('.')
        parts.reverse()
        candidates = tld_tree_path(parts, self.tldtree)
        if len(candidates) == 0:
            return None
        candidates.reverse()
        tldparts = []
        leaf = False
        for part in candidates:
            if part[1]:
                leaf = True
            if leaf:
                tldparts.append(part[0])
        tld = '.'.join(tldparts)
        return tld

    def get_tld_count(self, fqdn: str) -> int:
        """returns the number of tld parts for domain, eg.
        example.com -> 1
        bla.co.uk -> 2"""
        tld = self.get_tld(fqdn)
        if tld is None:
            return 0
        return len(tld.split('.'))

    def get_domain(self, fqdn: str) -> str:
        """returns the domain name with all subdomains stripped.
         eg, TLD + one label
         """
        hostlabels, tld = self.split(fqdn)
        if len(hostlabels) > 0:
            return f'{hostlabels[-1]}.{tld}'
        else:
            return tld

    def split(self, fqdn: str) -> tp.Tuple[tp.List[str], str]:
        """split the fqdn into hostname labels and tld. returns a 2-tuple, the first element is a list of hostname lablels, the second element is the tld
        eg.: foo.bar.baz.co.uk returns (['foo','bar','baz'],'co.uk')
        """
        tldcount = self.get_tld_count(fqdn)
        labels = fqdn.split('.')
        return labels[:-tldcount], '.'.join(labels[-tldcount:])

    def add_tld(self, tld: str) -> None:
        """add a new tld to the list"""
        tld = tld.lower().strip('.')
        parts = tld.split('.')
        parts.reverse()
        update = tld_list_to_tree(parts)
        self.tldtree = tld_tree_update(self.tldtree, update)

    def add_tlds_from_file(self, filename: str) -> None:
        for tld in load_tld_file(filename):
            self.add_tld(tld)


if __name__ == '__main__':
    t = TLDMagic()
    t.add_tld('bay.livefilestore.com')
    t.add_tld('co.uk')

    for test in ['kaboing.bla.bay.livefilestore.com', 'yolo.doener.com', 'blubb.co.uk', 'bloing.bazinga', 'co.uk']:
        print("'%s' -> '%s'" % (test, t.get_tld(test)))
