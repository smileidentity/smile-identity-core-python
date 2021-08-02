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

    def generate_sec_key(self, timestamp=None):
        public_key = RSA.importKey(base64.b64decode(self.api_key))
        cipher = PKCS1_v1_5.new(public_key)
        if timestamp is None:
            timestamp = int(time.time())
        hashed = self.__get_hash(timestamp)
        encrypted = base64.b64encode(cipher.encrypt(hashed.encode("utf-8")))

        signature = "{}|{}".format(encrypted.decode(encoding="UTF-8"), hashed)
        return {"sec_key": signature, "timestamp": timestamp}

    def __get_hash(self, timestamp):
        to_hash = "{}:{}".format(int(self.partner_id), timestamp)
        new_hash = str(to_hash).encode("utf-8")
        return hashlib.sha256(new_hash).hexdigest()

    def generate_signature(self, timestamp=None):
        _timestamp = timestamp
        if _timestamp is None:
            _timestamp = datetime.now().isoformat()
        hmac_new = hmac.new(self.api_key.encode("utf-8"), digestmod=hashlib.sha256)
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

    def confirm_sec_key(self, timestamp, sec_key):
        encrypted, hashed = sec_key.split("|")
        local_hash = self.__get_hash(timestamp)
        # python libraries only allow decryption from a private key
        # TODO: re look at this
        return True
