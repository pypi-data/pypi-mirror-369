import abc
import inspect
from typing import Any

from tamm.utils.json import JSONSerializableABCMixin


class Preprocessor(JSONSerializableABCMixin, json_namespace="preprocessor"):
    """
    Abstract base class for all preprocessors

    The signature of init function will become the serialized json 'config'.
    All __init__ arguments must be saved as instance attributes for JSON serialization
    to work.

    For example,

    .. code-block:: python

        class MyPreprocessor(_Preprocessor):

            def __init__(
                self,
                attribute1 = "value1"
                attribute2 = "value2"
            ):
                self.attribute1 = attribute1 # required for json serialization
                self.attribute2 = attribute2 # required for json serialization

    will serialize into

    .. code-block:: json

        {
            "__tamm_type__": "preprocessor:MyPreprocessor",
            "attribute1": "value1",
            "attribute2": "value1",
        }

    """

    @abc.abstractmethod
    def __call__(self, *example: Any) -> Any:
        """
        Process one example

        Args:
            example: Raw data of any Python class which can be preprocessed by concrete
                     preprocessor

        Returns: Any preprocessed object
        """

    def __eq__(self, other):
        if other is None:
            return False
        return self.__dict__ == other.__dict__

    def _to_json_dict_impl(self) -> dict:
        """
        Default serializer implementation of all preprocessor.
        Serializes all ``__init__`` arguments, which are essentially preprocessor
        config, to dict.

        Assumes all __init__ arguments be kept track of, as instance attributes
        """
        init_signature = inspect.signature(self.__init__)  # type: ignore[misc]
        init_arguments = list(init_signature.parameters.items())
        init_arguments = [
            (k, v)
            for k, v in init_arguments
            if v.kind not in {v.VAR_KEYWORD, v.VAR_POSITIONAL}
        ]
        if not init_arguments:
            return {}
        config_attrs = {}
        for p, _ in init_arguments:
            try:
                config_attrs[p] = getattr(self, p)
            except AttributeError as e:
                raise TypeError(
                    f"Cannot JSON serialize '{self.__class__.__name__}' "
                    f"instance because __init__  argument '{p}' isn't kept track of "
                    f"as instance attribute"
                ) from e
        return self._omit_defaults(config_attrs)

    def _omit_defaults(self, attr_dict: dict) -> dict:
        attr_dict = attr_dict.copy()
        init_signature = inspect.signature(self.__init__)  # type: ignore[misc]
        attrs_with_default_value = []
        for k, v in attr_dict.items():
            try:
                if v == init_signature.parameters[k].default:
                    attrs_with_default_value.append(k)
            except KeyError:
                pass
        for attr_to_remove in attrs_with_default_value:
            attr_dict.pop(attr_to_remove)
        return attr_dict

    @classmethod
    def _from_json_dict_impl(cls, **raw_dict) -> "Preprocessor":
        """
        De-serializes all attributes from dict by passing them through ``__init__``

        Args:
            **raw_dict: Dictionary representation (i.e., config)
                        of this preprocessor

        Returns: ``Preprocessor``

        """
        new_instance = cls(**raw_dict)
        return new_instance
