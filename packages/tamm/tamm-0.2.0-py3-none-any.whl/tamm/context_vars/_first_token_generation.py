import contextlib as _contextlib

# Global bool to replace ContextVar for torch.compile compatibility
_first_token_generation_flag: bool = False


def get_first_token_generation_flag() -> bool:
    """
    Returns whether we are currently generating the first token in a sequence.

    Returns:
        bool: ``True`` if we're generating the first token, ``False`` otherwise
    """
    return _first_token_generation_flag


@_contextlib.contextmanager
def first_token_generation_context():
    """
    Context manager for indicating first token generation.

    Sets a flag ``True`` indicating that we're generating the first token in a sequence.
    The flag is automatically reset to ``False`` when exiting the context.

    Example:
        >>> with first_token_generation_context():
        ...     first_token_logits = model(input_ids, ...)
    """
    global _first_token_generation_flag  # pylint: disable=global-statement
    old_value = _first_token_generation_flag
    _first_token_generation_flag = True
    try:
        yield
    finally:
        _first_token_generation_flag = old_value
