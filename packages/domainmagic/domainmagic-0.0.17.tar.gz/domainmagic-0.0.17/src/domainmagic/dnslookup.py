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
import threading
from dns import resolver
from dns.rdatatype import to_text as rdatatype_to_text
from .tasker import get_default_threadpool, TaskGroup, TimeOut
from .util import get_logger
import time
import typing as tp
import logging


class DNSLookupResult:

    def __init__(self) -> None:
        self.qtype = None
        self.question = None
        self.name = None
        self.content = None
        self.ttl = None
        self.rtype = None

    def __str__(self) -> str:
        return str(self.content)

    def __repr__(self) -> str:
        return "<type='%s' content='%s' ttl='%s'>" % (self.rtype, self.content, self.ttl)


def _make_results(question: tp.Union[str, bytes], qtype: str, resolveranswer: resolver.Answer) -> tp.List[DNSLookupResult]:
    results = []
    for answer in resolveranswer:
        dnr = DNSLookupResult()
        dnr.question = question
        dnr.qtype = qtype
        dnr.content = answer.to_text()
        dnr.ttl = resolveranswer.rrset.ttl
        dnr.rtype = rdatatype_to_text(resolveranswer.rdtype)
        results.append(dnr)

    return results


class DNSLookup:
    MAX_PARALLEL_REQUESTS = 100

    semaphore = threading.Semaphore(MAX_PARALLEL_REQUESTS)

    def __init__(self, nameservers: tp.Optional[tp.List[resolver.Resolver]] = None, timeout: float = 3, lifetime: float = 10, logprefix: str = '') -> None:
        self.nameservers = nameservers

        if self.nameservers is None:
            self.resolver = resolver.Resolver()
        else:
            self.resolver = resolver.Resolver(configure=False)
            self.resolver.nameservers = self.nameservers
            # print self.resolver.nameservers

        self.resolver.timeout = timeout   # timeout for a individual request before retrying
        self.resolver.lifetime = lifetime  # max time for a request

        self.logger = get_logger(__name__, logprefix)

    def lookup(self, question: tp.Union[str, bytes], qtype: str = 'A') -> tp.List[DNSLookupResult]:
        """lookup one record returns a list of DNSLookupResult"""
        if isinstance(question, bytes):
            question = question.decode()
        assert isinstance(question, str)

        resolveranswer = None

        try:
            DNSLookup.semaphore.acquire(False)
            self.logger.debug(f"query: {question}/{qtype}")
            resolveranswer = self.resolver.resolve(question, qtype)
            self.logger.debug(
                f"query {question}/{qtype} completed -> {' / '.join([x.to_text() for x in resolveranswer.rrset])}")
        except resolver.NXDOMAIN:
            pass
        except resolver.NoAnswer:
            pass
        except Exception as e:
            # TODO: some dnspython exceptions don't have a description - maybe add the full stack?
            self.logger.warning(f"dnslookup {question}/{qtype} failed: {e.__class__.__name__}: {str(e)}")
        finally:
            DNSLookup.semaphore.release()

        if resolveranswer is not None:
            results = _make_results(question, qtype, resolveranswer)
            return results
        else:
            return []

    def lookup_multi(self, questions: tp.Iterable[str], qtype: str = 'A', timeout: float = 10) -> tp.Dict[str, tp.List[DNSLookupResult]]:
        """lookup a list of multiple records of the same qtype. the lookups will be done in parallel
        returns a dict question->[list of DNSLookupResult]
        """

        tg = TaskGroup()
        for question in questions:
            tg.add_task(self.lookup, args=(question, qtype))

        threadpool = get_default_threadpool()
        threadpool.add_task(tg)

        try:
            tg.join(timeout)
        except TimeOut:
            self.logger.warning('timeout in lookup_multi')
            pass

        result = {}
        for task in tg.tasks:
            if task.done:
                result[task.args[0]] = task.result
            else:
                self.logger.warning(f"hanging lookup: {task}")

        # print("lookup multi, questions=%s, qtype=%s, result=%s"%(questions,qtype,result))
        threadpool.stayalive = False

        return result


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    d = DNSLookup()
    # print "Sync lookup:"
    # print d.lookup_sync('fuglu.org')

    print("lookup start")
    start = time.time()
    res = d.lookup_multi(['fuglu.org', 'heise.de', 'slashdot.org'])
    end = time.time()
    diff = end - start
    print("lookup end, time=%.4f" % diff)
    print(res)
