import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from smile_id_core import Signature, IdApi, ServerError


class TestIdApi(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.id_api = IdApi("001", self.public_key, 0)
        self.__reset_params()
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

    def __reset_params(self):
        self.partner_params = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": 5,
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
        self.options_params = {
            "return_job_status": True,
            "return_history": True,
            "return_images": True,
        }

    def test_instance(self):
        self.__reset_params()
        self.assertEqual(self.id_api.partner_id, "001")
        self.assertEqual(self.id_api.api_key, self.public_key)
        self.assertEqual(self.id_api.url, 'https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test')

    def test_no_partner_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(None, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through partner params")

    def test_no_id_info_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, None)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through ID Information")

    def test_invalid_job_type(self):
        self.__reset_params()
        self.partner_params["job_type"] = 1
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params, False)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you are setting your job_type to 5 to query ID Api")

    def test_id_info_params(self):
        self.__reset_params()
        self.id_info_params["country"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"key country cannot be empty")

        self.__reset_params()
        self.id_info_params["id_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"key id_type cannot be empty")

        self.__reset_params()
        self.id_info_params["id_number"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"key id_number cannot be empty")

    def get_id_response(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        return {"JSONVersion": "1.0.0",
                "SmileJobID": "0000000324",
                "PartnerParams": {
                    "job_id": "D7t4PtgWk9kl",
                    "user_id": "fffafbdc-073f-44b1-81f5-588866124ae2",
                    "job_type": 5
                },
                "ResultType": "ID Verification",
                "ResultText": "ID Number Validated",
                "ResultCode": "1012",
                "IsFinalResult": "true",
                "Actions": {
                    "Verify_ID_Number": "Verified",
                    "Return_Personal_Info": "Returned"
                },
                "Country": "NG",
                "IDType": "PASSPORT",
                "IDNumber": "A00000000",
                "ExpirationDate": "2024-02-13",
                "FullName": "DOE LEO JOE",
                "DOB": "2000-09-20",
                "Photo": "/9j/4AAQSAAAAAD//gASSVJJP/bAEMABAMDAw/wCUUP/Z",
                "PhoneNumber": "Not Available",
                "Gender": "Male",
                "Address": "Not Available",
                "FullData":
                    {

                    },
                "Source": "ID API",
                "timestamp": timestamp,
                "signature": sec_timestamp["sec_key"]
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

    def test_error_return_data(self):
        self.__reset_params()
        with self.assertRaises(ServerError) as ve:
            with patch('requests.post') as mocked_post, patch('requests.get') as mocked_get:
                mocked_post.return_value.status_code = 400
                mocked_post.return_value.ok = True
                mocked_post.return_value.text.return_value = {'code': '2204', 'error': 'unauthorized'}
                mocked_post.return_value.json.return_value = {'code': '2204', 'error': 'unauthorized'}

                mocked_get.return_value.status_code = 200
                mocked_get.return_value.ok = True
                mocked_get.return_value.text.return_value = TestIdApi._get_smile_services_response()
                mocked_get.return_value.json.return_value = TestIdApi._get_smile_services_response()

                response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0],
                         u"Failed to post entity to https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test/id_verification, status=400, response={'code': '2204', 'error': 'unauthorized'}")

    def test_validate_return_data(self):
        self.__reset_params()
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self.get_id_response()
            mocked_post.return_value.json.return_value = self.get_id_response()

            response = self.id_api.submit_job(self.partner_params, self.id_info_params, False)

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.json())
