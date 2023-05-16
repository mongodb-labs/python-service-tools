"""Default logging configuration for structlog."""

from enum import IntEnum, Enum, auto
import logging
import logging.config
import sys
import threading
from types import TracebackType
from typing import Any, Dict, Iterable, Optional, Type
from _thread import _ExceptHookArgs as ExceptHookArgs

import structlog

TEXT_LOG_FORMAT = "[%(levelname)s %(filename)s:%(funcName)s:%(lineno)s] %(message)s"
VERBOSE_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


class LogFormat(Enum):
    """Format to write logs in."""

    JSON = auto()
    TEXT = auto()


class Verbosity(IntEnum):
    """Verbosity level for logging. The higher the level the more logging we do."""

    WARNING = 0
    INFO = 1
    DEBUG = 2
    MAX = 3

    def level(self) -> int:
        """
        Get the `logging` level for this verbosity.

        :return: logging level.
        """
        v = self.value
        return VERBOSE_LEVELS[v] if v < len(VERBOSE_LEVELS) else VERBOSE_LEVELS[-1]


def _log_uncaught_thread_exceptions(args: ExceptHookArgs) -> None:
    """Handle logging uncaught exceptions in threads."""
    _log_uncaught_exceptions(args.exc_type, args.exc_value, args.exc_traceback)


def _log_uncaught_exceptions(
    exception_class: Type[BaseException],
    exception: Optional[BaseException] = None,
    trace: Optional[TracebackType] = None,
) -> None:
    """Handle logging uncaught exceptions."""
    log = structlog.get_logger()

    log.critical(
        "Uncaught exception",
        exc_info=(exception_class, exception, trace),
    )


def default_logging(
    verbosity: int,
    log_format: LogFormat = LogFormat.TEXT,
    external_logs: Optional[Iterable[str]] = None,
    loggers_to_configure: Optional[Iterable[str]] = None,
) -> None:
    """
    Configure structlog based on the given parameters.

    Logging will be done to stdout.

    :param verbosity: Amount of verbosity to use.
    :param log_format: Format to logs should be written in.
    :param external_logs: External modules that should have logging turned down unless verbosity is
        set to highest level.
    :param loggers_to_configure: Names of loggers to configure with the same configuration.
    """
    level = Verbosity(verbosity).level()

    if log_format == LogFormat.TEXT:
        logging.basicConfig(level=level, stream=sys.stdout, format=TEXT_LOG_FORMAT)
        structlog.configure(
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
        )
    elif log_format == LogFormat.JSON:
        # Setup json logging.
        logger_config = {"handlers": ["json"], "level": level}
        loggers = build_loggers_dictionary(loggers_to_configure, logger_config)
        logging.config.dictConfig(
            {
                "version": 1,
                "formatters": {
                    "json": {
                        "format": "%(message)s $(lineno)d $(filename)s",
                        "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    }
                },
                "handlers": {"json": {"class": "logging.StreamHandler", "formatter": "json"}},
                "loggers": loggers,
            }
        )

        structlog.configure(
            context_class=structlog.threadlocal.wrap_dict(dict),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
            ],
        )

    # Unless the user specifies higher verbosity than we have levels, turn down the log level
    # for external libraries.
    if external_logs and verbosity < Verbosity.MAX:
        # Turn down logging for modules outside this project.
        for logger in external_logs:
            logging.getLogger(logger).setLevel(logging.WARNING)

    # Log exceptions
    sys.excepthook = _log_uncaught_exceptions
    threading.excepthook = _log_uncaught_thread_exceptions


def build_loggers_dictionary(
    loggers: Optional[Iterable[str]], logger_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build a dictionary of loggers to configure.

    This will automatically include a default logger under `""`.

    :param loggers: List of log names to include in dictionary.
    :param logger_config: Configuration to use for logging.
    :return: Dictionary defining the logging configuration for each logger.
    """
    logger_dict = {"": logger_config}
    if loggers:
        logger_dict.update({logger: logger_config for logger in loggers})
    return logger_dict
