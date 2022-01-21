from http import HTTPStatus
from typing import Any

from fastapi import HTTPException


class WebsocketConnectError(HTTPException):
    def __init__(self, detail: Any, status_code: int = HTTPStatus.BAD_REQUEST):
        self.status_code = status_code
        self.detail = detail


class AuthError(WebsocketConnectError):
    def __init__(self, detail: Any, status_code: int = HTTPStatus.BAD_REQUEST):
        self.status_code = status_code
        self.detail = detail


class InvalidTokenError(AuthError):
    def __init__(self, detail: Any, status_code: int = HTTPStatus.BAD_REQUEST):
        self.status_code = status_code
        self.detail = detail
