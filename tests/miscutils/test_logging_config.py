import logging

import miscutils.logging_config as under_test
from miscutils.testing import relative_patch_maker

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
