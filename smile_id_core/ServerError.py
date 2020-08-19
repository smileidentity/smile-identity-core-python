__all__ = ['ServerError']


class ServerError(Exception):
    def __init__(self, message):
        self.message = message
