import logging

import miscutils.logging_config as under_test


class TestVerbosity:
    def test_logging_warning(self):
        assert under_test.Verbosity.WARNING.level() == logging.WARNING

    def test_logging_info(self):
        assert under_test.Verbosity.INFO.level() == logging.INFO

    def test_logging_debug(self):
        assert under_test.Verbosity.DEBUG.level() == logging.DEBUG

    def test_logging_max(self):
        assert under_test.Verbosity.MAX.level() == logging.DEBUG
