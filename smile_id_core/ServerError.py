"""ServerError Class."""
__all__ = ["ServerError"]


class ServerError(Exception):
    """Server error handling."""

    def __init__(self, message: str):
        """Return message string."""
        self.message = message
