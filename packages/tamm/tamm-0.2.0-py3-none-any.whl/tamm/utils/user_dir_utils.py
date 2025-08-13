"""
utils.user_dir_utils
====================

This module implements helper functions for working with |tamm|'s user dir.

.. autofunction:: tamm.utils.user_dir_utils.get_tamm_user_dir

.. autofunction:: tamm.utils.user_dir_utils.get_tamm_cache_dir

.. autofunction:: tamm.utils.user_dir_utils.get_tamm_lock_dir

.. autofunction:: tamm.utils.user_dir_utils.get_tamm_tmp_dir
"""

import os as _os

from tamm.runtime_configuration import rc as _rc


def get_tamm_user_dir() -> str:
    """
    Returns |tamm|'s user dir, creating the directory if it does not
    yet exist.  This path may be configured using :attr:`tamm.rc.user_dir`
    or the ``TAMM_USER_DIR`` env var.
    """
    return _maybe_make_dir(_rc.user_dir)


def get_tamm_cache_dir() -> str:
    """
    Returns |tamm|'s cache dir, creating the directory if it does not
    yet exist.  The cache dir is a local directory for caching downloads,
    and it is a subdirectory of the user dir.
    """

    result = _os.path.join(get_tamm_user_dir(), "cache")
    return _maybe_make_dir(result)


def get_tamm_lock_dir() -> str:
    """
    Returns |tamm|'s lock dir, creating the directory if it does not
    yet exist.  The lock dir is a local directory for |tamm| file locks,
    and it is a subdirectory of the user dir.
    """

    result = _os.path.join(get_tamm_user_dir(), "lock")
    return _maybe_make_dir(result)


def get_tamm_tmp_dir() -> str:
    """
    Returns |tamm|'s tmp dir, creating the directory if it does not
    yet exist.  The tmp dir is a local directory for |tamm| tmp files,
    and it is a subdirectory of the user dir.
    """

    result = _os.path.join(get_tamm_user_dir(), "tmp")
    return _maybe_make_dir(result)


def _maybe_make_dir(dirpath: str) -> str:
    if not _os.path.exists(dirpath):
        _os.makedirs(dirpath, exist_ok=True)
    return dirpath
