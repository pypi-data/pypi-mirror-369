from enum import Enum as _Enum


class OptionalBool(str, _Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    NOTSET = "NOTSET"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.upper()
            for member in cls:
                if member.value == value:
                    return member
        if value is True:
            return OptionalBool.TRUE
        if value is False:
            return OptionalBool.FALSE
        if value is None:
            return OptionalBool.NOTSET
        return None

    def __bool__(self):
        if self is OptionalBool.TRUE:
            return True
        if self is OptionalBool.FALSE:
            return False

        raise ValueError("OptionalBool.notset does not have a truth value")

    def __eq__(self, other) -> bool:
        """Overrides the default implementation"""
        if isinstance(other, OptionalBool):
            return self is other
        if isinstance(other, bool):
            return False if self is self.NOTSET else bool(self) is other
        if other is None:
            return self is OptionalBool.NOTSET

        raise ValueError("OptionalBool.notset can only compare with bool or None")

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __invert__(self):
        if self is OptionalBool.TRUE:
            return OptionalBool.FALSE
        if self is OptionalBool.FALSE:
            return OptionalBool.TRUE
        raise ValueError(f"Cannot invert {self}")
