import warnings

import wrapt

warnings.filterwarnings("always", category=DeprecationWarning, module=r"^tamm\..*")


def deprecate(alternative=None, *, name=None):
    @wrapt.decorator
    def wrapper(wrapped, _instance, args, kwargs):
        nonlocal name

        if alternative is not None:
            alternative_message = f" Please use {alternative} instead."
        else:
            alternative_message = ""
        if name is None:
            name = wrapped.__name__

        msg = (
            f"{name} will be removed in a future version of tamm."
            f"{alternative_message}"
        )

        warnings.warn(msg, category=DeprecationWarning, stacklevel=2)

        return wrapped(*args, **kwargs)

    return wrapper


def deprecation(message: str):
    warnings.warn(message, category=DeprecationWarning, stacklevel=2)
