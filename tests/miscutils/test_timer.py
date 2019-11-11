from unittest.mock import MagicMock

import miscutils.timer as under_test


class TestTimer:
    def test_timing_written_to_log(self):
        logger = MagicMock()

        @under_test.timer(logger)
        def sample_fn():
            return True

        assert sample_fn()

        logger.log.assert_called_once()
