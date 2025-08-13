import abc
import logging as _logging
import tempfile as _tempfile
from pathlib import Path as _Path
from typing import ContextManager

from tamm import _helpers
from tamm.utils import user_dir_utils as _user_dir_utils
from tamm.utils.uri._helpers import _get_dest_path_from_uri, atomic_download_prefix

_logger = _logging.getLogger(__name__)


class BaseURLHandler(metaclass=abc.ABCMeta):
    name = "base"

    def __init__(self, use_cache=False):
        self.use_cache = use_cache

    def open(self, urlpath: str, /, *args, **kwargs) -> ContextManager:
        _logger.debug("Opening %s using %s", urlpath, self.__class__.__name__)
        local_path = self.map_to_local(urlpath)
        # pylint: disable-next=unspecified-encoding
        return open(local_path, *args, **kwargs)

    def map_to_local(self, uri: str) -> _Path:
        if not isinstance(uri, str):
            raise ValueError(f"uri must be a string, got {type(uri)}")

        return self._map_to_local(uri)

    @abc.abstractmethod
    def _map_to_local(self, uri: str) -> _Path:
        """
        Mapping a remote URI to a local Posix path

        Args:
            uri: source: URI to a file

        Returns: a local Posix path

        """


class AtomicDownloadURIHandler(BaseURLHandler, metaclass=abc.ABCMeta):
    """
    Abstract class for any URI handler that provides "downloading" functionality.
    """

    name = "atomic"

    @abc.abstractmethod
    def _download_uri_to_local_impl(self, uri: str, local_path: _Path) -> _Path:
        """
        Abstract method which downloads a remote URI to a local

        Args:
            uri: URI to be opened by the concrete downloader
            local_path: local path to write output file

        Returns: a local Posix path

        """

    def _download_uri_to_local(self, uri: str, local_path: _Path) -> _Path:
        _logger.debug(
            "Downloading %s to %s using %s", uri, local_path, self.__class__.__name__
        )

        return self._download_uri_to_local_impl(uri, local_path)

    def _map_to_local(self, uri: str) -> _Path:
        """
        Implements downloading with caching and multiprocess safety
        Downloads a file located by ``uri`` to a local path. If cache is enabled,
        the file is expected to be stored under a uri-hashed path under
        get_tamm_cache_dir(). Otherwise, the file is expected to be under
        get_tamm_tmp_dir() with random prefix.

        Args:
            uri: any valid URI

        Returns: a local Posix path

        """
        if _Path(uri).is_file():
            return _Path(uri)
        if uri.startswith("file://"):
            return _Path(uri[len("file://") :])

        dest_path = _get_dest_path_from_uri(uri)
        if self.use_cache and dest_path.is_file():
            _logger.debug(
                "[%s] %s local cache-hit",
                self.__class__.__name__,
                str(dest_path),
            )
            return dest_path

        if not self.use_cache:
            temp_prefix = _Path(
                _tempfile.mkdtemp(dir=_user_dir_utils.get_tamm_tmp_dir())
            )
            temp_prefix.mkdir(parents=True, exist_ok=True)
            temp_path = temp_prefix / dest_path.name
            self._download_uri_to_local(uri, temp_prefix / dest_path.name)
            return temp_path

        with _helpers.file_lock(dest_path.with_suffix(".write_lock")):
            if dest_path.is_file():
                # When a process acquires the lock, first check if the destination path
                # exists. If it exists, return immediately and *avoid*
                # repeated downloading
                return dest_path

            with atomic_download_prefix(dest_path) as temp_prefix:
                self._download_uri_to_local(uri, temp_prefix / dest_path.name)

        return dest_path
