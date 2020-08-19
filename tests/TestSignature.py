import hashlib
import time
import unittest
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

from smile_id_core import Signature


class TestSignature(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

    def test_partner_id_api_key(self):
        self.assertEqual(self.signatureObj.partner_id, self.partner_id)
        self.assertEqual(self.public_key, self.signatureObj.decoded_api_key)

    def test_generate_sec_key(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        self.assertEqual(sec_timestamp["timestamp"], timestamp)

        hashed = hashlib.sha256('{}:{}'.format(int(self.partner_id), timestamp).encode('utf-8')).hexdigest()
        encrypted, hashed2 = sec_timestamp["sec_key"].split("|")
        self.assertEqual(hashed, hashed2)

    # TODO: Confirm sec key tests
    def test_confirm_sec_key(self):
        pass
