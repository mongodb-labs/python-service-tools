import logging
import sys

from structlog.testing import capture_logs

import servicetools.logging_config as under_test
from servicetools.testing import relative_patch_maker

patch = relative_patch_maker(under_test.__name__)


class TestVerbosity:
    def test_logging_warning(self):
        assert under_test.Verbosity.WARNING.level() == logging.WARNING

    def test_logging_info(self):
        assert under_test.Verbosity.INFO.level() == logging.INFO

    def test_logging_debug(self):
        assert under_test.Verbosity.DEBUG.level() == logging.DEBUG

    def test_logging_max(self):
        assert under_test.Verbosity.MAX.level() == logging.DEBUG


class TestDefaultConfiguration:
    @patch("structlog.configure")
    @patch("logging.basicConfig")
    def test_text_logging(self, mock_basic_config, mock_configure):
        under_test.default_logging(
            under_test.Verbosity.WARNING, log_format=under_test.LogFormat.TEXT
        )
        mock_basic_config.assert_called_once()
        mock_configure.assert_called_once()

    @patch("structlog.configure")
    @patch("logging.config.dictConfig")
    def test_json_logging(self, mock_dict_config, mock_configure):
        under_test.default_logging(
            under_test.Verbosity.WARNING, log_format=under_test.LogFormat.JSON
        )
        mock_dict_config.assert_called_once()
        mock_configure.assert_called_once()

    @patch("logging.getLogger")
    def test_external_logs(self, mock_get_logger):
        under_test.default_logging(
            under_test.Verbosity.DEBUG,
            under_test.LogFormat.JSON,
            external_logs=["some_external_log"],
        )
        mock_get_logger.assert_called_with("some_external_log")
        mock_get_logger.return_value.setLevel.assert_called_with(logging.WARNING)


class TestBuildLoggersDictionary:
    def test_no_loggers_should_include_default(self):
        logger_config = {"config": "my config"}

        logger_dict = under_test.build_loggers_dictionary(None, logger_config)

        assert logger_dict == {"": logger_config}

    def test_multiple_loggers_should_be_included(self):
        logger_config = {"config": "my config"}
        loggers = [f"logger_{i}" for i in range(5)]

        logger_dict = under_test.build_loggers_dictionary(loggers, logger_config)

        assert logger_dict[""] == logger_config
        for logger in loggers:
            assert logger_dict[logger] == logger_config


class TestExceptionLogging:
    def test_exceptions_are_logged(self):
        under_test.default_logging(
            under_test.Verbosity.WARNING, log_format=under_test.LogFormat.TEXT
        )
        assert sys.excepthook is under_test._log_uncaught_exceptions
        with capture_logs() as captured:
            under_test._log_uncaught_exceptions(Exception, Exception("This is an exception"), ())
            assert len(captured) == 1
            assert captured[0]["event"] == "Uncaught exception"
            assert captured[0]["log_level"] == "critical"
            assert captured[0]["exc_info"][1].args[0] == "This is an exception"
