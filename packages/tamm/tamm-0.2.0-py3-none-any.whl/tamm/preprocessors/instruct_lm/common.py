import dataclasses as _dataclasses
from typing import List as _List
from typing import Union as _Union


@_dataclasses.dataclass
class InstructLMPreprocessorOutput:
    """A return type for instruct LM preprocessors in |tamm|."""

    input_ids: _List[int]
    """A list of tokenized prompt ids."""

    label_ids: _Union[_List[int], None]
    """
    An optional list of label ids.  This may be ``None`` during inference.
    """
