__all__ = ['SmileIdError']


class SmileIdError(Exception):
    def __init__(self, message):
        self.message = message
