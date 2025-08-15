# -*- coding: utf-8 -*-
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

# noinspection PyUnresolvedReferences
import os  # pycharm sez is unused, but that's very wrong
import time
import errno
import logging

logging.warning('domainmagic.filelock module is deprecated and will be removed. use fcntl.flock instead.')


class FileLockException(Exception):
    pass


class FileLock:
    """ A file locking mechanism that has context-manager support so
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """

    def __init__(self, file_name, timeout=10, delay=.05, stale_timeout=30):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        self.fd = None
        self.is_locked = False
        self.lockfile = "%s.lock" % file_name
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay

        self.clear_stale(stale_timeout)

    def clear_stale(self, stale_timeout):
        """ Clear stale lock files if they are older than stale_timeout seconds
        """
        if os.path.exists(self.lockfile):
            stat = os.stat(self.lockfile)
            now = time.time()
            ctime = stat.st_ctime
            if now - ctime > stale_timeout:
                os.unlink(self.lockfile)

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    raise FileLockException("Timeout occured.")
                time.sleep(self.delay)
        self.is_locked = True

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        # noinspection PyGlobalUndefined
        global os  # required when called from __del__
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            self.is_locked = False

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()


def runtest():
    try:
        with FileLock("/tmp/todelete.txt", timeout=0, delay=.05, stale_timeout=30):
            print("%u: with filelock..." % os.getpid())
            time.sleep(1)
    except FileLockException:
        print("%u: file is already locked" % os.getpid())


if __name__ == '__main__':
    import multiprocessing
    p = multiprocessing.Process(target=runtest)
    p.start()
    runtest()
    p.join()
