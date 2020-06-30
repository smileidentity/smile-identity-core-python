import hashlib
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

from src import Signature, Utilities, PartnerParameters, Options


class TestSignature(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())
        self.partner_params = PartnerParameters(str(uuid4()), str(uuid4()), 1)
        self.utilities = Utilities(self.partner_id, self.public_key, 0)
        self.options_params = Options(None, True, True, True)

    def test_instance(self):
        self.assertEqual(self.utilities.partner_id, "001")
        self.assertEqual(self.utilities.api_key, self.public_key)
        self.assertEqual(self.utilities.url, 'https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test')

    def _get_job_status_response(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        return {
            "timestamp": timestamp,
            "signature": sec_timestamp["sec_key"],
            "job_complete": True,
            "job_success": True,
            "result": {
                "ResultText": "Enroll User",
                "ResultType": "SAIA",
                "SmileJobID": "0000001897",
                "JSONVersion": "1.0.0",
                "IsFinalResult": "true",
                "PartnerParams": {
                    "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                    "user_id": "e54e0e98-8b8c-4215-89f5-7f9ea42bf650",
                    "job_type": 4
                },
                "ConfidenceValue": "100",
                "IsMachineResult": "true",
            },
            "image_links": {
                "selfie_image": "https://smile-fr-results.s3.us-west-2.amazonaws.com/test/000000/023/023-0000001897-LoRSpxJUzmYgYS2R00XpaHJYLOiNXN/SID_Preview_FULL.jpg"
            },
            "code": "2302",
            "history": [
                {
                    "ResultCode": "1210",
                    "ResultText": "Enroll User",
                    "ResultType": "DIVA",
                    "SmileJobID": "0000000857",
                    "JSONVersion": "1.0.0",
                    "IsFinalResult": "true",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info"
                    }
                },
                {
                    "ResultCode": "0814",
                    "ResultText": "Provisional Enroll - Under Review",
                    "SmileJobID": "0000000857",
                    "ConfidenceValue": "97.000000",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                    }
                },
                {
                    "DOB": "1990-01-01",
                    "IDType": "BVN",
                    "Country": "Nigeria",
                    "FullName": "Peter Parker",
                    "ExpirationDate": "Not Available",
                    "IDNumber": "A01234567",
                    "ResultCode": "1012",
                    "ResultText": "ID Validated",
                    "ResultType": "ID Verification",
                    "SmileJobID": "0000000857",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                        "ExpirationDate": "Not Available"
                    }
                }
            ]
        }

    def test_no_partner_params(self):
        with self.assertRaises(ValueError) as ve:
            response = self.utilities.get_job_status(None, self.partner_params.get("job_id"), None)
        self.assertEqual(ve.exception.args[0], u"user_id cannot be empty")

        with self.assertRaises(ValueError) as ve:
            response = self.utilities.get_job_status(self.partner_params.get("user_id"), None, None)
        self.assertEqual(ve.exception.args[0], u"job_id cannot be empty")

        with patch('requests.post') as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self._get_job_status_response()
            mocked_post.return_value.json.return_value = self._get_job_status_response()

            job_status = self.utilities.get_job_status(self.partner_params.get("user_id"),
                                                       self.partner_params.get("job_id"),
                                                       None)
            job_status_response = job_status.json()

            self.assertEqual(job_status.status_code, 200)
            self.assertIsNotNone(job_status.json())

    def test_response(self):
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self._get_job_status_response()
            mocked_post.return_value.json.return_value = self._get_job_status_response()

            job_status = self.utilities.get_job_status(self.partner_params.get("user_id"),
                                                       self.partner_params.get("job_id"),
                                                       self.options_params)
            job_status_response = job_status.json()

            self.assertEqual(job_status.status_code, 200)
            self.assertIsNotNone(job_status.json())
