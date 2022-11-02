import sys

if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

from smile_id_core.IdApi import IdApi
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.Utilities import Utilities
from smile_id_core.WebApi import WebApi

__version__ = importlib_metadata.version(__package__)
__all__ = ["IdApi", "Signature", "Utilities", "WebApi", "ServerError"]
