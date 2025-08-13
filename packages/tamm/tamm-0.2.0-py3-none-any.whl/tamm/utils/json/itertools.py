from typing import Any as _Any
from typing import Callable as _Callable
from typing import Generator as _Generator
from typing import Optional as _Optional

from tamm.utils.json.api import _get_json_dumps_default

_DEFAULT_JSON_LEAF_TYPES = (str, int, float, bool, type(None))
_DEFAULT_JSON_TYPES = (*_DEFAULT_JSON_LEAF_TYPES, dict, list, tuple)


def iter_json_serializable(
    obj: _Any, *, default: _Optional[_Callable[[_Any], _Any]] = None
) -> _Generator[_Any, None, None]:
    """
    Recursively yields objects within a JSON-serializable object.
    The function understands serializable |tamm| objects, consistent with
    :func:`.tamm.utils.json.dumps`.

    Args:
        obj: The object to iterate over.
        default (:obj:`callable`, optional): An optional ``default`` arg
            to handle new object types. The interface is the same as the
            ``default`` argument for Python's``json.dumps``.

    Returns:
        A generator that recursively yields objects from ``obj``.

    Raises:
        TypeError: If ``obj`` is not JSON-serializable.

    Example:

        .. code-block:: python

            >>> x = [{"a": [1, 2]}, "b"]
            >>> for y in iter_json_serializable(x):
            ...     print(y)
            ...
            [{'a': [1, 2]}, 'b']
            {'a': [1, 2]}
            [1, 2]
            1
            2
            b
    """
    default = _get_json_dumps_default(default=default)
    return _iter_json_serializable_helper(obj, default=default)


def _iter_json_serializable_helper(
    obj: _Any, *, default: _Callable[[_Any], _Any]
) -> _Generator[_Any, None, None]:
    yield obj

    if not isinstance(obj, _DEFAULT_JSON_TYPES):
        obj = default(obj)
        if not isinstance(obj, _DEFAULT_JSON_TYPES):
            raise TypeError(f"Unrecognized type {type(obj)}")

    if isinstance(obj, _DEFAULT_JSON_LEAF_TYPES):
        return

    if isinstance(obj, dict):
        obj = obj.values()

    for value in obj:
        yield from _iter_json_serializable_helper(value, default=default)
