from datetime import datetime
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class Signature:
    def __init__(self, partner_id, api_key) -> None:
        self.partner_id = partner_id
        self.api_key = api_key

    def generate_sec_key(self):
        decoded_api_key = base64.b64decode(self.api_key)
        partner_id = self.partner_id
        timestamp = datetime.isoformat(datetime.utcnow())
        hashed = hashlib.sha256('{}:{}'.format(int(partner_id), timestamp)).hexdigest()
        ## Note: python does not handle RSA keys natively we have used the pycrypto library
        public_key = RSA.importKey(decoded_api_key)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted = base64.b64encode(cipher.encrypt(hashed))
        signature = "{}|{}".format(encrypted, hashed)
        return {
            "sec_key": signature,
            "timestamp": timestamp
        }

    def confirm_sec_key(self, timestamp, sec_key):
        encrypted, hashed = sec_key.split("|")
        local_hashed = hashlib.sha256('{}:{}'.format(int(self.partner_id), timestamp)).hexdigest()
        return hashed == base64.b64encode(
            RSA.decrpy(encrypted, base64.b64decode(self.api_key))) and hashed == local_hashed
