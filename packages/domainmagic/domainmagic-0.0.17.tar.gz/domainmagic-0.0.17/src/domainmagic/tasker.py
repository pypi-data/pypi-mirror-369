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
import time
import typing as tp


class Task:

    """Default task object used by the threadpool
    """

    def __init__(self, method:tp.Callable, args:tp.Optional[tp.Iterable[tp.Any]]=None, kwargs:tp.Optional[tp.MutableMapping[str, tp.Any]]=None, comment: tp.Optional[str] = None) -> None:
        self.method = method

        if args is not None:
            self.args = args
        else:
            self.args = ()

        if kwargs is not None:
            self.kwargs = kwargs
        else:
            self.kwargs = {}

        self.comment = comment

        self.done = False
        """will be set to true after the task has been executed"""

        self.result = None
        """contains the result of the method call after the task has been executed"""

    def handlesession(self, worker) -> None:
        self.result = self.method(*self.args, **self.kwargs)
        self.done = True

    def __repr__(self) -> str:
        return "<Task method='%s' args='%s' kwargs='%s' done=%s comment=%s >" % (self.method, self.args, self.kwargs, self.done, self.comment)


class TimeOut(Exception):
    pass


class TaskGroup:

    """Similar to Task, but can be used to run multiple methods in parallel
    """

    def __init__(self) -> None:
        self.tasks: tp.List[Task] = []

    def add_task(self, method:tp.Callable, args:tp.Optional[tp.Iterable[tp.Any]]=None, kwargs:tp.Optional[tp.MutableMapping[str, tp.Any]]=None, comment: tp.Optional[str] = None) -> Task:
        """add a method call to the task group. and return the task object.
        the resulting task object should *not* be modified by the caller
        and should not be added to a threadpool again, this will be done automatically when the taskgroup is added to the threadpool
        """
        t = Task(method, args=args, kwargs=kwargs, comment=comment)
        self.tasks.append(t)
        return t

    def handlesession(self, worker) -> None:
        """add all tasks to the thread pool"""
        for task in self.tasks:
            worker.pool.add_task(task)

    def join(self, timeout:tp.Optional[float]=None) -> None:
        """block until all tasks in this group are done"""
        starttime = time.time()
        while True:
            if timeout is not None:
                if time.time() - starttime > timeout:
                    raise TimeOut()

            if self.all_done():
                return
            time.sleep(0.01)

    def all_done(self) -> bool:
        for task in self.tasks:
            if not task.done:
                return False
        return True


default_threadpool = None


def get_default_threadpool():
    global default_threadpool
    if default_threadpool is None:
        # import here to prevent circular import
        from domainmagic.threadpool import ThreadPool
        default_threadpool = ThreadPool(
            minthreads=20,
            maxthreads=100,
            queuesize=100)
    return default_threadpool
