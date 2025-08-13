import contextlib as _contextlib
import hashlib as _hashlib
import shutil as _shutil
import tempfile as _tempfile
from pathlib import Path as _Path

from tamm.utils import user_dir_utils


def _get_dest_prefix_from_uri(uri: str) -> _Path:
    uri = str(uri)  # coerce uri into a string
    sha256_uri = _hashlib.sha256(uri.strip().encode("utf-8")).hexdigest()
    return _Path(user_dir_utils.get_tamm_cache_dir()) / sha256_uri[:2] / sha256_uri[2:]


def _get_dest_path_from_uri(uri: str) -> _Path:
    dest_prefix = _get_dest_prefix_from_uri(uri)
    basename = _Path(uri).name
    return dest_prefix / basename


@_contextlib.contextmanager
def atomic_download_prefix(dest_path: _Path):
    """
    Provides a temporary prefix for downloader to write into and then move the file
    over to the destination.

    Args:
        dest_path: Expected destination path
    """
    basename = dest_path.name
    dest_prefix_temp = _Path(_tempfile.mkdtemp(dir=user_dir_utils.get_tamm_tmp_dir()))
    dest_prefix_temp.mkdir(parents=True, exist_ok=True)
    yield dest_prefix_temp
    # Download to temp and then move to cache to ensure atomicity. PR #664
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    _shutil.move(str(dest_prefix_temp / basename), dest_path)
