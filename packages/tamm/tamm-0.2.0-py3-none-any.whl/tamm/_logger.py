import logging as _logging

from tamm.runtime_configuration import rc as _rc


def get_logger(name: str = _rc.PROJECT_SLUG):
    return _logging.getLogger(name)


def set_logger_formatter(logger):
    try:
        import coloredlogs  # pylint: disable=import-outside-toplevel

        formatter = coloredlogs.ColoredFormatter(fmt=_rc.log_format)
    except Exception as e:
        logger.debug("Failed to use colored logs due to exception: %s", e)
        formatter = _logging.Formatter(fmt=_rc.log_format)
    for handler in logger.handlers:
        handler.setFormatter(formatter)


def init_logger(name: str = _rc.PROJECT_SLUG):
    logger = get_logger(name=name)
    logger.propagate = False
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(_logging.StreamHandler())
    log_level = _rc.log_level
    log_level = log_level.upper() if isinstance(log_level, str) else log_level
    logger.setLevel(log_level)
    set_logger_formatter(logger)
    return logger
