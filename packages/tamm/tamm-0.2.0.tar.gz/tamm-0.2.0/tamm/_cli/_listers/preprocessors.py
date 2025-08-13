from tamm import preprocessors
from tamm._cli._listers._base import BaseLister


class PreprocessorLister(BaseLister):
    name = "preprocessors"

    def print(self):
        print("\n".join(preprocessors.list()))
