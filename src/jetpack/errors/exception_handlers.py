import logging as logger
from typing import Callable, Dict, List

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from jetpack.errors import GenericErrors


class ExceptionHandlers:
    @staticmethod
    def generic_exception_handler(_: Request, exc: Exception):
        logger.exception(f"Generic Exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Something went wrong. Please contact support."},
        )

    @staticmethod
    def request_validation_exception_handler(_: Request, exc: RequestValidationError):
        logger.exception(f"Request Validation Exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"message": "Request Validation Error", "detail": exc.errors()},
        )

    @staticmethod
    def exception_handler_generator(exception: GenericErrors):
        def exception_handler(_: Request, exc: GenericErrors):
            logger.exception(f"{exception.__name__}: {exc}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": exc.message},
            )

        return exception_handler


def get_exception_handlers(
    exceptions_list: List[Exception] = None,
    custom_validation_handler: Callable = None,
    exception_handlers: Dict = None,
):
    handlers = {
        RequestValidationError: custom_validation_handler
        or ExceptionHandlers.request_validation_exception_handler,
        Exception: ExceptionHandlers.generic_exception_handler,
    }
    handlers.update(exception_handlers or {})
    if exceptions_list:
        for exception in exceptions_list:
            handlers.update(
                {exception: ExceptionHandlers.exception_handler_generator(exception)}
            )


__all__ = ["get_exception_handlers"]
