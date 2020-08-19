import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core import Signature, Utilities


class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())
        self.__reset_params()
        self.utilities = Utilities(self.partner_id, self.public_key, 0)

    def __reset_params(self):
        self.partner_params = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": 1,
        }
        self.id_info_params = {
            "first_name": "FirstName",
            "middle_name": "LastName",
            "last_name": "MiddleName",
            "country": "NG",
            "id_type": "PASSPORT",
            "id_number": "A00000000",
            "dob": "1989-09-20",
            "phone_number": "",
            "entered": True,
        }
        self.image_params = []
        self.image_params.append({"image_type_id": "2", "image": "base6image"})
        self.options_params = {
            "return_job_status": True,
            "return_history": True,
            "return_images": True,
        }

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

    @staticmethod
    def _get_smile_services_response():
        return {
            "id_types": {
                "NG": {
                    "NIN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id"
                    ],
                    "CAC": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "company",
                        "job_id"
                    ],
                    "TIN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id"
                    ],
                    "VOTER_ID": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id"
                    ],
                    "BVN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id"
                    ],
                    "PHONE_NUMBER": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name"
                    ],
                    "DRIVERS_LICENSE": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob"
                    ],
                    "PASSPORT": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob"
                    ]
                },
            }
        }

    def test_no_partner_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(None)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through partner params")

    def test_missing_partner_params(self):
        self.__reset_params()
        self.partner_params["user_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        value_exception = ve.exception
        self.assertEqual(value_exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.__reset_params()
        self.partner_params["job_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.__reset_params()
        self.partner_params["job_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

    def test_id_info_params(self):
        self.__reset_params()
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.status_code = 200
            mocked_get.return_value.ok = True
            mocked_get.return_value.text.return_value = TestUtilities._get_smile_services_response()
            mocked_get.return_value.json.return_value = TestUtilities._get_smile_services_response()

            self.id_info_params["country"] = None
            with self.assertRaises(ValueError) as ve:
                Utilities.validate_id_params(self.utilities.url, self.id_info_params, self.partner_params)
            self.assertEqual(ve.exception.args[0], u"country cannot be empty")

            self.__reset_params()
            self.id_info_params["country"] = "ZW"
            with self.assertRaises(ValueError) as ve:
                Utilities.validate_id_params(self.utilities.url, self.id_info_params, self.partner_params)
            self.assertEqual(ve.exception.args[0], u"country ZW is invalid")

            self.__reset_params()
            self.id_info_params["id_type"] = None
            with self.assertRaises(ValueError) as ve:
                Utilities.validate_id_params(self.utilities.url, self.id_info_params, self.partner_params)
            self.assertEqual(ve.exception.args[0], u"id_type cannot be empty")

            self.__reset_params()
            self.id_info_params["id_number"] = None
            with self.assertRaises(ValueError) as ve:
                Utilities.validate_id_params(self.utilities.url, self.id_info_params, self.partner_params)
            self.assertEqual(ve.exception.args[0], u"key id_number cannot be empty")

    def test_response(self):
        self.__reset_params()
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self._get_job_status_response()
            mocked_post.return_value.json.return_value = self._get_job_status_response()

            job_status = self.utilities.get_job_status(self.partner_params, self.options_params,
                                                       sec_timestamp["sec_key"], timestamp)
            job_status_response = job_status.json()

            self.assertEqual(job_status.status_code, 200)
            self.assertIsNotNone(job_status.json())
