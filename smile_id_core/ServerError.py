"""ServerError Class."""

from typing import Optional

from requests import Response

__all__ = ["ServerError"]


class ServerError(Exception):
    """Server error handling."""

    # The failed HTTP response, when there is one
    response: Optional[Response] = None

    def __init__(self, message: str):
        """Return message string."""
        self.message = message
