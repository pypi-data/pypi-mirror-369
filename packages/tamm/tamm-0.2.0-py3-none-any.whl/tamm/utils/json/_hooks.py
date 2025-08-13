import abc
import importlib.metadata
from collections import OrderedDict as _OrderedDict
from typing import Protocol as _Protocol

import packaging.requirements


class JSONDictHook(_Protocol):
    @abc.abstractmethod
    def __call__(self, json_dict: dict) -> dict:
        """
        Classes conform to this protocol should process a json encodable dictionary to
        json encodable dictionary.
        This class intends to define an interface for arbitrary transformation
        needed for json encodable dictionaries
        Args:
            json_dict:

        Returns: a json encodable dict

        """


class ReadabilityHook(JSONDictHook):
    def __init__(self):
        # below is the order that will appear in JSON
        self.attributes_to_bring_forward = [
            "__tamm_type__",
            "__package_requirements__",
            "model_id",
            "description",
            "is_deprecated",
            "replacement_model_id",
        ]
        # flip the order because this operates like a stack
        self.attributes_to_bring_forward.reverse()

    def __call__(self, json_dict: dict):
        json_list = sorted(json_dict.items())
        ordered_dict = _OrderedDict(json_list)
        for key in self.attributes_to_bring_forward:
            try:
                ordered_dict.move_to_end(key, last=False)
            except KeyError:
                pass
        return dict(ordered_dict)


class PackageRequirementsHook(JSONDictHook):
    def __call__(self, json_dict: dict):
        try:
            package_requirements = json_dict.pop("__package_requirements__")
        except KeyError:
            return json_dict
        if package_requirements is not None:
            for requirement_str in package_requirements:
                requirement = packaging.requirements.Requirement(requirement_str)
                package_version = importlib.metadata.version(requirement.name)
                if requirement.specifier.contains(package_version, prereleases=True):
                    continue
                raise RuntimeError(
                    "Attempted to deserialize a tamm object that requires "
                    f"'{requirement_str}', but you have {requirement.name} version "
                    f"{package_version}."
                )
        return json_dict


class UnusedAttributeHook(JSONDictHook):
    def __call__(self, json_dict: dict):
        json_dict.pop("__tamm_type__", None)
        return json_dict
