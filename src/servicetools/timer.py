"""Utilities to get timing information."""
import logging
from time import perf_counter
from typing import Callable, Any

import structlog

LOGGER = structlog.get_logger(__name__)


def timer(logger: Any = LOGGER, details: bool = False, level: int = logging.INFO) -> Callable:
    """
    Decorate a function to log how log the function took to execute.

    :param logger: structlog logger to write to.
    :param details: include function parameters in log.
    :param level: logging level to log at.
    """

    def decorator(fn: Callable) -> Callable:
        def measure_time(*args: Any, **kwargs: Any) -> Any:
            start_time = perf_counter()
            result = fn(*args, **kwargs)
            end_time = perf_counter()

            seconds = end_time - start_time
            detailed_args = {}
            if details:
                detailed_args["fn_args"] = args
                detailed_args["fn_kwargs"] = kwargs  # type: ignore
            logger.log(
                level, "timing information", function=fn.__name__, seconds=seconds, **detailed_args
            )

            return result

        return measure_time

    return decorator
