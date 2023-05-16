"""Starlette middleware for services."""
import logging
from time import perf_counter
from typing import Any, Callable, Awaitable, Set, Optional

from structlog import get_logger
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message

LOGGER = get_logger(__name__)


class StructlogRequestMiddleware(BaseHTTPMiddleware):
    """
    Logs information to a structlog logger about each HTTP request.

    Logging will occur at the start and completion of each request.

    If a request throws an exception, it will be logged and converted to a 500
    response.

    Any failures responses (400s and 500s) will be logged. A set of failure
    codes to ignore can be provided to not log certain error codes (for example,
    ignore all 404 errors).
    """

    def __init__(
        self,
        app: ASGIApp,
        dispatch: Optional[DispatchFunction] = None,
        logger: Any = LOGGER,
        log_level: int = logging.INFO,
        ignored_status_codes: Optional[Set[int]] = None,
        include_request_in_failed_requests: Optional[bool] = False,
    ) -> None:
        """
        Create structlog request middleware.

        :param app: Web application.
        :param dispatch: Dispatch function.
        :param logger: Structlog logger to log to.
        :param log_level: Log level to write at.
        :param ignored_status_codes: Set of status codes to not report on.
        :param include_request_in_failed_requests: Whether to ignore the request in failed calls.
        """
        super().__init__(app, dispatch)
        self.logger = logger
        self.log_level = log_level
        self.include_request_in_failed_requests = include_request_in_failed_requests
        self.ignored_status_codes = ignored_status_codes or set()

    def __log(self, msg: str, **kwargs: Any) -> None:
        """Log at the configured level."""
        self.logger.log(self.log_level, msg, **kwargs)

    @staticmethod
    async def set_body(request: Request) -> None:
        """
        Set the body of the request so that it can be read multiple times.

        :param request: The request to set the body of.
        """
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Log information about the request and call the next layer."""
        method = request.method
        endpoint = request.url.path

        await self.set_body(request)
        request_body = await request.body()

        self.__log("HTTP request start", method=method, endpoint=endpoint)
        start_time = perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            self.__log("Exception Occurred", exc_info=True)
            raise e

        end_time = perf_counter()
        duration = end_time - start_time
        status_code = response.status_code

        self.__log(
            "HTTP request end",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            seconds=duration,
        )
        if (
            status_code >= status.HTTP_400_BAD_REQUEST
            and status_code not in self.ignored_status_codes
        ):
            if self.include_request_in_failed_requests:
                self.__log(
                    "HTTP request error",
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    request=request_body,
                )
            else:
                self.__log(
                    "HTTP request error", method=method, endpoint=endpoint, status_code=status_code
                )
        return response
