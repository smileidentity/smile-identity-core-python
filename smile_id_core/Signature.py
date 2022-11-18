import base64
import hashlib
import hmac
from datetime import datetime

__all__ = ["Signature"]


class Signature:
    def __init__(self, partner_id: str, api_key: str):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key

    def generate_signature(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        hmac_new = hmac.new(self.api_key.encode("utf-8"), digestmod=hashlib.sha256)
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(self.partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))
        calculated_signature = base64.b64encode(hmac_new.digest())
        return {
            "signature": calculated_signature.decode("utf-8"),
            "timestamp": timestamp,
        }

    def confirm_signature(self, timestamp: str, msg_signature: str) -> bool:
        return self.generate_signature(timestamp)["signature"] == msg_signature
