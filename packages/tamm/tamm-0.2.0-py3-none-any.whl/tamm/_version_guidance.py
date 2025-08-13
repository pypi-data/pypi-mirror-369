import importlib.metadata as _importlib_metadata
import logging as _logging
from typing import Union as _Union

import packaging.requirements as _packaging_requirements
from packaging.version import parse as _parse_version

from tamm._version import __version__ as _TAMM_VERSION
from tamm.runtime_configuration import rc as _rc

_logger = _logging.getLogger(__name__)


def _get_tamm_dist() -> _importlib_metadata.Distribution:
    """Returns the tamm distribution"""
    tamm_ver = _parse_version(_TAMM_VERSION)
    distributions = [
        dist
        for dist in _importlib_metadata.distributions()
        if _parse_version(dist.version) == tamm_ver
    ]

    for dist in distributions:
        try:
            top_level_text = dist.read_text("top_level.txt")
        except Exception as e:
            _logger.debug(f"Caught exception reading top_level.txt for {dist}: {e}")
            continue

        if _rc.PROJECT_SLUG in top_level_text.split():
            return dist

    raise RuntimeError("Unable to locate the tamm distribution")


def _get_specifier_set(
    dist: _importlib_metadata.Distribution, *, package_name
) -> _Union[_packaging_requirements.SpecifierSet, None]:
    """
    Returns the specfier set for the ``dist`` requirement with name ``package_name``.
    Returns ``None`` if the package is not a requirement
    """
    requirements = (_packaging_requirements.Requirement(req) for req in dist.requires)
    for requirement in requirements:
        if requirement.name == package_name:
            return requirement.specifier
    return None


def _get_min_version(
    specifier_set: _packaging_requirements.SpecifierSet,
) -> _Union[str, None]:
    """
    Returns the version lower bound for a requirement and ``None`` if it does not exist.
    """
    for specifier in specifier_set:
        if specifier.operator == ">=":
            return specifier.version
    return None


def _get_python_requirement() -> _packaging_requirements.SpecifierSet:
    """Returns the version specfier set for tamm's Python requirement."""
    dist = _get_tamm_dist()
    python_requirement = dist.metadata["Requires-Python"]
    return _packaging_requirements.SpecifierSet(python_requirement)


def get_min_python_version() -> str:
    """Returns the Python version lower-bound for the tamm package."""
    spec_set = _get_python_requirement()
    return _get_min_version(spec_set)


def _get_torch_requirement() -> _packaging_requirements.SpecifierSet:
    """Returns the version specfier set for tamm's torch requirement."""
    dist = _get_tamm_dist()
    return _get_specifier_set(dist, package_name="torch")


def get_min_torch_version() -> str:
    """Returns the torch version lower-bound for the tamm package."""
    spec_set = _get_torch_requirement()
    return _get_min_version(spec_set)
