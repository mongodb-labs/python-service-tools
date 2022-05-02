from asyncio import Future
from unittest.mock import MagicMock

import pytest

import servicetools.middleware as under_test


def create_mock_request() -> MagicMock:
    url = MagicMock(path="fake-path")
    request = MagicMock(method="POST", url=url)
    request_wrapper = Future()
    request_body = "fake-body"
    request_wrapper.set_result(request_body)
    request.body.return_value = request_wrapper
    request._receive.return_value = request_wrapper
    return request


def create_mock_response_wrapper(status_code: int) -> MagicMock:
    response = MagicMock(status_code=status_code)
    response_wrapper = Future()
    response_wrapper.set_result(response)
    return response_wrapper


class TestStructlogRequestMiddleWare:
    @pytest.mark.asyncio
    async def test_start_and_end_requests_logged(self):
        request = create_mock_request()

        response_wrapper = create_mock_response_wrapper(200)
        logger = MagicMock()

        middleware = under_test.StructlogRequestMiddleware(MagicMock(), logger=logger)

        await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 2

    @pytest.mark.asyncio
    async def test_exception_logging(self):
        request = create_mock_request()

        logger = MagicMock()

        def throw_error(_):
            raise ValueError("Throwing an error")

        middleware = under_test.StructlogRequestMiddleware(MagicMock(), logger=logger)

        with pytest.raises(ValueError):
            await middleware.dispatch(request, throw_error)

        assert logger.log.call_count == 2

    @pytest.mark.asyncio
    async def test_error_logging(self):
        request = create_mock_request()

        response_wrapper = create_mock_response_wrapper(404)
        logger = MagicMock()

        middleware = under_test.StructlogRequestMiddleware(MagicMock(), logger=logger)

        await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 3

    @pytest.mark.asyncio
    async def test_error_logging_include_request(self):
        request = create_mock_request()

        response_wrapper = create_mock_response_wrapper(400)
        logger = MagicMock()

        middleware = under_test.StructlogRequestMiddleware(
            MagicMock(), logger=logger, include_request_in_failed_requests=True
        )

        await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 3
        assert logger.log.mock_calls[2][2]["request"] == "fake-body"

    @pytest.mark.asyncio
    async def test_ignored_error_logging(self):
        request = create_mock_request()

        response_wrapper = create_mock_response_wrapper(404)
        logger = MagicMock()

        middleware = under_test.StructlogRequestMiddleware(
            MagicMock(), logger=logger, ignored_status_codes={404}
        )

        await middleware.dispatch(request, lambda _: response_wrapper)

        assert logger.log.call_count == 2
