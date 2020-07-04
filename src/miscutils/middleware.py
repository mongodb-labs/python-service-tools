"""Starlette middleware for services."""
import logging
from time import perf_counter
from typing import Any, Callable, Awaitable, Set, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class StructlogReqestMiddleware(BaseHTTPMiddleware):
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
        logger: Any,
        log_level: int = logging.INFO,
        ignored_status_codes: Optional[Set[int]] = None,
    ) -> None:
        """
        Create structlog request middleware.

        :param logger: Structlog logger to log to.
        :param log_level: Log level to write at.
        :param ignored_status_codes: Set of status codes to not report on.
        """
        self.logger = logger
        self.log_level = log_level
        self.ignored_status_codes = ignored_status_codes or set()

    def __log(self, msg: str, **kwargs: Any) -> None:
        """Log at the configured level."""
        self.logger.log(self.log_level, msg, **kwargs)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Log information about the request and call the next layer."""
        method = request.method
        endpoint = request.url.path

        self.__log("HTTP request start", method=method, endpoint=endpoint)
        start_time = perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            self.__log("Exception Occurred", exc_info=True)
            response = JSONResponse(
                {"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            self.__log(
                "HTTP request error",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                content=response.body,
            )

        return response
