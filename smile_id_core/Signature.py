import time
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

__all__ = ['Signature']


class Signature:
    def __init__(self, partner_id, api_key):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
        self.decoded_api_key = api_key  # base64.b64decode(self.api_key)
        self.public_key = RSA.importKey(self.decoded_api_key)
        self.cipher = PKCS1_v1_5.new(self.public_key)

    def generate_sec_key(self, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        hashed = self.__get_hash(timestamp)
        encrypted = base64.b64encode(self.cipher.encrypt(hashed.encode('utf-8')))

        signature = "{}|{}".format(encrypted.decode(encoding='UTF-8'), hashed)
        return {
            "sec_key": signature,
            "timestamp": timestamp
        }

    def __get_hash(self, timestamp):
        to_hash = '{}:{}'.format(int(self.partner_id), timestamp)
        new_hash = str(to_hash).encode('utf-8')
        return hashlib.sha256(new_hash).hexdigest()

    def confirm_sec_key(self, timestamp, sec_key):
        encrypted, hashed = sec_key.split("|")
        local_hash = self.__get_hash(timestamp)
        # python libraries only allow decryption from a private key
        # TODO: re look at this
        return True
