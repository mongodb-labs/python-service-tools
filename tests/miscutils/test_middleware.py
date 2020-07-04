from asyncio import Future
from unittest.mock import MagicMock

import pytest

import miscutils.middleware as under_test


class TestStructlogRequestMiddleWare:
    @pytest.mark.asyncio
    async def test_start_and_end_requests_logged(self):
        request = MagicMock()
        response = MagicMock(status_code=200)
        response_wrapper = Future()
        response_wrapper.set_result(response)
        logger = MagicMock()

        middleware = under_test.StructlogReqestMiddleware(logger)

        response = await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 2

    @pytest.mark.asyncio
    async def test_exception_logging(self):
        request = MagicMock()
        response = MagicMock(status_code=200)
        response_wrapper = Future()
        response_wrapper.set_result(response)
        logger = MagicMock()

        def throw_error(_):
            raise ValueError("Throwing an error")

        middleware = under_test.StructlogReqestMiddleware(logger)

        response = await middleware.dispatch(request, throw_error)

        assert logger.log.call_count == 4

    @pytest.mark.asyncio
    async def test_error_logging(self):
        request = MagicMock()
        response = MagicMock(status_code=404)
        response_wrapper = Future()
        response_wrapper.set_result(response)
        logger = MagicMock()

        middleware = under_test.StructlogReqestMiddleware(logger)

        response = await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 3

    @pytest.mark.asyncio
    async def test_ignored_error_logging(self):
        request = MagicMock()
        response = MagicMock(status_code=404)
        response_wrapper = Future()
        response_wrapper.set_result(response)
        logger = MagicMock()

        middleware = under_test.StructlogReqestMiddleware(logger, ignored_status_codes={404})

        response = await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 2
