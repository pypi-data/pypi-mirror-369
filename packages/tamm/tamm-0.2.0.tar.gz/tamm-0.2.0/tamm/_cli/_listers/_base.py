import abc as _abc


class BaseLister(metaclass=_abc.ABCMeta):
    name = "unnamed"
    # pylint: disable=redefined-builtin

    def __init__(self, all, long, wide, show_deprecated):
        self.all = all
        self.long = long
        self.wide = wide
        self.show_deprecated = show_deprecated or all

    @_abc.abstractmethod
    def print(self):
        ...
