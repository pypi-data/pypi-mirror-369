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
import time
import os
import tempfile
import zlib
import zipfile
import tarfile
import datetime
import fcntl
from io import BytesIO
from .util import get_logger
from urllib.request import build_opener
from urllib import parse as urlparse
import typing as tp


DATEFORMAT = "%a, %d %b %Y %X UTC"


class FileTooSmallException(Exception):
    pass


class FileExtractionException(Exception):
    pass


class NoUpdateAvailable(Exception):
    pass


class FileUpdaterMultiproc:
    """
    Make sure this object exist only once per process
    """

    instance = None
    procPID = None

    def __init__(self, logprefix: str = '') -> None:
        FileUpdaterMultiproc.check_replace_instance(logprefix)

    @classmethod
    def check_replace_instance(cls, logprefix: str = '') -> None:
        pid = os.getpid()
        logger = get_logger(__name__, logprefix)
        if pid == cls.procPID and cls.instance is not None:
            # logger.debug("Return existing FileUpdater Singleton for process with pid: %u"%pid)
            pass
        else:
            if cls.instance is None:
                logger.debug("Create FileUpdater Singleton for process with pid: %u" % pid)
            elif cls.procPID != pid:
                logger.debug("Replace FileUpdater Singleton(created by process %u) for process with pid: %u" %
                             (cls.procPID, pid))

            cls.instance = FileUpdater()
            cls.procPID = pid

    def __getattr__(self, name: str) -> tp.Any:
        """Pass all queries to FileUpdater instance"""
        FileUpdaterMultiproc.check_replace_instance()
        return getattr(FileUpdaterMultiproc.instance, name)


class FileUpdater:

    def __init__(self, logprefix: str = '') -> None:
        # key: local absolute path
        # value: dict:
        # - update_url
        # - refresh_time
        # - minimum_size
        # - lock (threading.Lock object, created by add_file)
        self.defaults = {
            'refresh_time': 86400,
            'minimum_size': 0,
        }
        self.filedict = {}
        self.logger = get_logger(__name__, logprefix)

    def id(self) -> int:
        """Small helper function go get id of of actual instance in FileUpdaterMultiproc"""
        return id(self)

    def add_file(self, local_path: str, update_url: str, refresh_time: tp.Optional[int] = None, minimum_size: tp.Optional[int] = None, unpack: bool = False, filepermission: tp.Optional[int] = None) -> None:
        if local_path not in self.filedict:
            self.filedict[local_path] = {
                'refresh_time': refresh_time or self.defaults['refresh_time'],
                'minimum_size': minimum_size or self.defaults['minimum_size'],
                'unpack': unpack,
                'update_url': update_url,
                'filepermission': filepermission,
                'logprefix': self.logger.prefix,
            }

            self.update_in_thread(local_path)
        else:
            self.logger.debug(f"adding file {local_path} -> already registered, not doing anything")

    @staticmethod
    def file_modtime(local_path: str) -> float:
        """returns the file modification timestamp"""
        statinfo = os.stat(local_path)
        return max(statinfo.st_ctime, statinfo.st_mtime)

    @staticmethod
    def file_age(local_path: str) -> float:
        """return the file age in seconds"""
        return time.time() - FileUpdater.file_modtime(local_path)

    def is_recent(self, local_path: str) -> bool:
        """returns True if the file mod time is within the configured refresh_time"""
        if not os.path.exists(local_path):
            return False

        return self.file_age(local_path) < self.filedict[local_path]['refresh_time']

    @staticmethod
    def has_write_permission(local_path: str) -> bool:
        perm = True
        if os.path.exists(local_path):
            if not os.access(local_path, os.W_OK):
                perm = False
            else:
                uid = os.getuid()
                stats = os.stat(local_path)
                if stats.st_uid != uid:
                    perm = False
        else:
            dirname = os.path.dirname(local_path)
            if not os.path.exists(dirname) or not os.access(dirname, os.W_OK):
                perm = False
        return perm

    def update(self, local_path: str, force: bool = False) -> None:
        # still use update in thread, but apply a timeout
        # so the code can not get stuck
        self.update_in_thread(local_path, force=force, timeout=66.0)

    @staticmethod
    def _unpack_tar(archive_content: bytes, archive_name: str, local_path: str) -> tp.Optional[bytes]:
        mode = 'r'
        if archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
            mode = 'r:gz'
        if archive_name.endswith('.tar.bz2'):
            mode = 'r:bz2'
        if archive_name.endswith('.tar.xz'):  # python 3 only
            mode = 'r:xz'

        content = None
        payload = BytesIO(archive_content)
        zf = tarfile.open(fileobj=payload, mode=mode)
        filenames = zf.getnames()
        for filename in filenames:
            if os.path.basename(filename) == os.path.basename(local_path):
                f = zf.extractfile(filename)
                content = f.read()
                f.close()
                break
        zf.close()
        return content

    @staticmethod
    def _unpack_zip(archive_content: bytes, local_path: str) -> bytes:
        content = None
        payload = BytesIO(archive_content)
        zf = zipfile.ZipFile(payload)
        filenames = zf.namelist()
        for filename in filenames:
            if os.path.basename(filename) == os.path.basename(local_path):
                content = zf.read(filename)
                break
        zf.close()
        return content

    @staticmethod
    def _get_lastfetched(local_path: str) -> tp.Optional[datetime.datetime]:
        ts = None
        if os.path.exists(local_path):
            mtime = os.stat(local_path).st_mtime
            ts = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
        return ts

    def download_file(self, update_url: str, timeout: float, local_path: tp.Optional[str] = None) -> bytes:
        self.logger.debug(f"open url: {update_url} with timeout: {timeout}")
        opener = build_opener()
        addheaders = []
        lastfetched = 0
        if local_path:
            lastfetched = self._get_lastfetched(local_path)
            if lastfetched:
                addheaders.append(('If-Modified-Since', lastfetched.strftime(DATEFORMAT)))
        opener.addheaders = addheaders
        url_info = opener.open(update_url, timeout=timeout)
        if url_info.code == 200:
            content = url_info.read()
            self.logger.debug(f"{len(content)} bytes downloaded from {update_url}")
        elif url_info.code == 304:
            self.logger.debug(f"no new data since {lastfetched} on {update_url}")
            raise NoUpdateAvailable
        else:
            content = None
            self.logger.debug(f"unexpected http code {url_info.code} from {update_url}")
        opener.close()
        return content

    def unpack(self, update_url: str, local_path: tp.Optional[str], content: bytes) -> bytes:
        u = urlparse.urlparse(update_url)
        path = u.path.lower()
        if path.endswith('.tar') or path.endswith('.tar.gz') or path.endswith('.tgz') \
                or path.endswith('.tar.bz2') or path.endswith('.tar.xz'):
            content = self._unpack_tar(content, path, local_path)
            print(len(content))
        elif path.endswith('.gz'):
            content = zlib.decompress(content, zlib.MAX_WBITS | 16)
        elif path.endswith('.zip'):
            content = self._unpack_zip(content, local_path)
        else:
            self.logger.debug(f'URL {update_url} does not seem to be a (supported) archive, not unpacking')
        return content

    def try_update_file(self, local_path: str, force: bool = False) -> None:
        # if the file is current, do not update
        if self.is_recent(local_path) and not force:
            self.logger.debug(f"File {local_path} is current - not updating")
            return

        if not self.has_write_permission(local_path):
            self.logger.debug(f"Can't write file {local_path} - not updating")
            return

        filedownload_timeout = 30
        self.logger.debug(f"Updating {local_path} - try to acquire lock")
        with open(local_path+".lock", 'a') as file_lock:
            try:
                fcntl.flock(file_lock.fileno(), fcntl.LOCK_EX)
                self.logger.debug(f"Updating {local_path} - lock acquire successfully")
                # check again in case we were waiting for the lock before and some
                # other thread just updated the file
                if self.is_recent(local_path) and not force:
                    self.logger.debug(f"File {local_path} got updated by a different thread - not updating")
                    fcntl.flock(file_lock.fileno(), fcntl.LOCK_UN)
                    return

                try:
                    update_url = self.filedict[local_path]['update_url']
                    content = self.download_file(update_url, filedownload_timeout)
                    handle, tmpfilename = tempfile.mkstemp()
                    if not content or len(content) < self.filedict[local_path]['minimum_size']:
                        fcntl.flock(file_lock.fileno(), fcntl.LOCK_UN)
                        raise FileTooSmallException(
                            f"file size {len(content)} downloaded from {update_url} is smaller than configured minimum of {self.filedict[local_path]['minimum_size']} bytes")
                    # TODO: add rar etc here
                    # http://stackoverflow.com/questions/3122145/zlib-error-error-3-while-decompressing-incorrect-header-check
                    if self.filedict[local_path]['unpack']:
                        content = self.unpack(update_url, local_path, content)
                    if content is None:
                        fcntl.flock(file_lock.fileno(), fcntl.LOCK_UN)
                        raise FileExtractionException(
                            f'failed to extract file {os.path.basename(local_path)} as {local_path} from file downloaded from {update_url}')

                    with os.fdopen(handle, 'wb') as f:
                        f.write(content)

                    # now change file permission
                    filepermission = self.filedict[local_path]['filepermission']
                    if filepermission is not None:
                        self.logger.debug(f'Set filepermission: {bin(filepermission)[2:]}')
                        try:
                            os.chmod(tmpfilename, filepermission)
                        except OSError:
                            pass
                    else:
                        self.logger.debug("Default file permission")

                    try:
                        os.rename(tmpfilename, local_path)
                    except OSError:
                        if os.path.exists(tmpfilename):
                            os.remove(tmpfilename)
                except NoUpdateAvailable:
                    pass
                except Exception as e:
                    self.logger.error(f'failed to update {local_path} due to {e.__class__.__name__}: {str(e)}')
            except OSError:
                self.logger.debug(
                    f"File {local_path} currently seems being updated by a different thread/process - not updating")
            finally:
                fcntl.flock(file_lock.fileno(), fcntl.LOCK_UN)
                if os.path.exists(local_path+".lock"):
                    os.remove(local_path+".lock")

    def update_in_thread(self, local_path: str, force: bool = False, timeout: float = -1) -> bool:
        th = threading.Thread(target=self.try_update_file, args=(local_path, force))
        th.daemon = True
        th.start()

        complete = True
        # wait for thread to complete if there's a timeout
        if timeout >= 0:
            th.join(timeout)
            try:
                complete = not th.is_alive()
            except AttributeError:
                # deprecated routine
                complete = not th.isAlive()
            if not complete:
                self.logger.error(f'Could not finish thread update_in_tread process to update {local_path}')
        return complete

    def wait_for_file(self, local_path: str, force_recent: bool = False) -> None:
        """make sure file :localpath exists locally.
        if it doesn't exist, it will be downloaded immediately and this call will block
        if it exists and force_recent is false, the call will immediately return
        if force_recent is true the age of the file is checked und the file will be re-downloaded in case it's too old"""

        if local_path not in self.filedict:
            raise ValueError(f"File {local_path} not configured for auto-updating - please call add_file first!")

        logger = get_logger(f'{__name__}.wait_for_file', self.logger.prefix)
        if os.path.exists(local_path):
            if self.is_recent(local_path):
                logger.debug(f'File exists and recent: {local_path}')
                return
            else:
                if force_recent:
                    logger.debug(f'File exists but not recent -> force update: {local_path}')
                    self.update(local_path)
                else:
                    logger.debug(f'File exists but not recent -> thread updater: {local_path}')
                    self.update_in_thread(local_path)
        else:
            logger.debug(f'File does not exist -> force update: {local_path}')
            self.update(local_path)


fileupdater = None


def updatefile(local_path: str, update_url: str, **outer_kwargs) -> tp.Callable:
    """decorator which automatically downlads/updates required files
    see fileupdate.Fileupdater.add_file() for possible arguments
    """
    def wrap(f: tp.Callable) -> tp.Callable:
        def wrapped_f(*args, **kwargs):
            global fileupdater
            if fileupdater is None:
                fileupdater = FileUpdaterMultiproc(logprefix=kwargs.get('logprefix', ''))

            force_recent = False

            if 'force_recent' in outer_kwargs:
                force_recent = True
                del outer_kwargs['force_recent']

            # add file if not already present
            fileupdater.add_file(local_path, update_url, **outer_kwargs)

            # wait for file
            fileupdater.wait_for_file(local_path, force_recent)
            return f(*args, **kwargs)

        return wrapped_f

    return wrap
