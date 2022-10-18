# from ._version import __version__
from smile_id_core.Utilities import Utilities
from smile_id_core.IdApi import IdApi
from smile_id_core.WebApi import WebApi
from smile_id_core.Signature import Signature
from smile_id_core.ServerError import ServerError

__version__ = "1.0.8"
__all__ = ["IdApi", "Signature", "Utilities", "WebApi", "ServerError"]

