"""MIT License

Copyright (c) 2024-2025 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Literal, Optional


class ChzzkpyException(Exception):
    pass


class LoginRequired(ChzzkpyException):
    """Exception that’s raised when a method need login."""

    def __init__(self):
        super(LoginRequired, self).__init__(
            "This method(feature) needs to login. Please use `login()` method."
        )


class BadRequestException(ChzzkpyException):
    """Exception that’s raised for when status code 400 occurs."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Invalid input value"
        super(BadRequestException, self).__init__(message)


class UnauthorizedException(ChzzkpyException):
    """Exception that’s raised for when status code 401 occurs."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Not Found"
        super(UnauthorizedException, self).__init__(message)


class ForbiddenException(ChzzkpyException):
    """Exception that’s raised for when status code 403 occurs."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Invalid permission"
        super(ForbiddenException, self).__init__(message)


class NotFoundException(ChzzkpyException):
    """Exception that’s raised for when status code 404 occurs."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Not Found"
        super(NotFoundException, self).__init__(message)


class TooManyRequestsException(ChzzkpyException):
    """Exception that’s raised for when status code 429 occurs."""

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Too many requests, try later."
        super(TooManyRequestsException, self).__init__(message)


class HTTPException(ChzzkpyException):
    """Exception that’s raised when an HTTP request operation fails."""

    def __init__(self, code: int, message: Optional[str] = None):
        if message is None:
            message = f"Reponsed error code ({code})"
        else:
            message += f" ({code})"
        super(HTTPException, self).__init__(message)


class ChatConnectFailed(ChzzkpyException):
    def __init__(self, message: str):
        super(ChatConnectFailed, self).__init__(message)

    @classmethod
    def websocket_upgrade_failed(cls):
        return cls("WebSocket upgrade failed: no PONG packet")

    @classmethod
    def polling_connect_failed(cls, status: int):
        return cls(f"Unexpected status code {status} in connect polling")

    @classmethod
    def max_connection(cls):
        return cls("Maximum number of sessions allowed to connect has been exceeded.")


class ReceiveErrorPacket(ChzzkpyException):
    def __init__(self, transport: Literal["polling", "websocket"], data: Any):
        super().__init__(
            f"{transport} type of connection received packet with an error. "
            f" (data: {self.code})"
        )

        self.current_transport = transport
        self.data = data
