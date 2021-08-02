import base64
import hashlib
import hmac
import time
import unittest
from datetime import datetime

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core import Signature


class TestSignature(unittest.TestCase):
    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.api_key = base64.b64encode(self.public_key).decode("UTF-8")
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.api_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

    def test_partner_id_api_key(self):
        self.assertEqual(self.signatureObj.partner_id, self.partner_id)
        # self.assertEqual(self.public_key, self.signatureObj.decoded_api_key)

    def test_generate_sec_key(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        self.assertEqual(sec_timestamp["timestamp"], timestamp)

        hashed = hashlib.sha256(
            "{}:{}".format(int(self.partner_id), timestamp).encode("utf-8")
        ).hexdigest()
        encrypted, hashed2 = sec_timestamp["sec_key"].split("|")
        self.assertEqual(hashed, hashed2)

    def test_generate_signature(self):
        timestamp = datetime.now().isoformat()
        signature = self.signatureObj.generate_signature(timestamp=timestamp)
        self.assertEqual(signature["timestamp"], timestamp)

        hmac_new = hmac.new(self.api_key.encode(), digestmod=hashlib.sha256)
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(self.partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))
        calculated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

        self.assertEqual(signature["signature"], calculated_signature)

    # TODO: Confirm sec key tests
    def test_confirm_sec_key(self):
        pass
