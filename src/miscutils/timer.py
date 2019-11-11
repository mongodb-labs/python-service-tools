"""Utilities to get timing information."""
from datetime import datetime
from typing import Callable

import structlog

LOGGER = structlog.get_logger(__name__)


def timer(logger=LOGGER, details: bool = False):
    """
    Decorate a function to log how log the function took to execute.

    :param logger: structlog logger to write to.
    :param details: include function parameters in log.
    """

    def decorator(fn: Callable):
        def measure_time(*args, **kwargs):
            start_time = datetime.now()
            result = fn(*args, **kwargs)
            end_time = datetime.now()

            seconds = (end_time - start_time).total_seconds()
            detailed_args = {}
            if details:
                detailed_args["fn_args"] = args
                detailed_args["fn_kwargs"] = kwargs
            logger.info(
                "timing information", function=fn.__name__, seconds=seconds, **detailed_args
            )

            return result

        return measure_time

    return decorator
