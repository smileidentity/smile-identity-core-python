import base64
import hashlib
import hmac
import time
from datetime import datetime

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

__all__ = ["Signature"]


class Signature:
    def __init__(self, partner_id: str, api_key: str):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key

    def generate_signature(self, timestamp=None):
        _timestamp = timestamp
        if _timestamp is None:
            _timestamp = datetime.now().isoformat()
        hmac_new = hmac.new(self.api_key, digestmod=hashlib.sha256)
        hmac_new.update(_timestamp.encode("utf-8"))
        hmac_new.update(str(self.partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))
        calculated_signature = base64.b64encode(hmac_new.digest())
        return {
            "signature": calculated_signature.decode("utf-8"),
            "timestamp": _timestamp,
        }

    def confirm_signature(self, timestamp, msg_signature):
        return self.generate_signature(timestamp)["signature"] == msg_signature
