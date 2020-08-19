import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core import WebApi, Signature, ServerError


class TestWebApi(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.__reset_params()
        self.web_api = WebApi("001", 'https://a_callback.com', self.public_key, 0)
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

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
        self.__reset_params()
        self.assertEqual(self.web_api.partner_id, "001")
        self.assertEqual(self.web_api.api_key, self.public_key)
        self.assertEqual(self.web_api.call_back_url, 'https://a_callback.com')
        self.assertEqual(self.web_api.url, 'https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test')

    def test_no_image_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, None,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through image details")

    def test_no_partner_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(None, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through partner params")

    def test_missing_partner_params(self):
        self.__reset_params()
        self.partner_params["user_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        value_exception = ve.exception
        self.assertEqual(value_exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.__reset_params()
        self.partner_params["job_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.__reset_params()
        self.partner_params["job_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

    def test_id_info_params(self):
        self.__reset_params()
        self.id_info_params["country"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"key country cannot be empty")

        self.__reset_params()
        self.id_info_params["id_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"key id_type cannot be empty")

        self.__reset_params()
        self.id_info_params["id_number"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"key id_number cannot be empty")

    def test_non_valid_image(self):
        self.__reset_params()
        self.image_params.append({"image_type_id": "0", "image": "path/to/image.jpg"})
        with self.assertRaises(FileNotFoundError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"No such file or directory path/to/image.jpg")

    def test_boolean_options_params_non_jt5(self):
        self.__reset_params()
        self.options_params["return_job_status"] = "Test"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params, False)
        self.assertEqual(ve.exception.args[0],
                         u"return_job_status needs to be a boolean")

        self.__reset_params()
        self.options_params["return_history"] = "tEST"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params, False)
        self.assertEqual(ve.exception.args[0],
                         u"return_history needs to be a boolean")

        self.__reset_params()
        self.options_params["return_images"] = "tEST"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params, False)
        self.assertEqual(ve.exception.args[0],
                         u"return_images needs to be a boolean")

    def _get_job_status_response(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        return {
            "upload_url": "https://some_url.com",
            "smile_job_id": "0000000857",
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

    def test_error_return_data(self):
        self.__reset_params()
        with self.assertRaises(ServerError) as ve:
            with patch('requests.post') as mocked_post:
                mocked_post.return_value.status_code = 400
                mocked_post.return_value.ok = True
                mocked_post.return_value.text.return_value = {'code': '2204', 'error': 'unauthorized'}
                mocked_post.return_value.json.return_value = {'code': '2204', 'error': 'unauthorized'}

                response = self.web_api.submit_job(self.partner_params, self.image_params,
                                                   self.id_info_params, self.options_params, False)
        self.assertEqual(ve.exception.args[0],
                         u"Failed to post entity to https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test/upload, status=400, response={'code': '2204', 'error': 'unauthorized'}")

    def test_validate_return_data(self):
        self.__reset_params()
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        with patch('requests.post') as mocked_post, patch('requests.put') as mocked_put:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self._get_job_status_response()
            mocked_post.return_value.json.return_value = self._get_job_status_response()

            mocked_put.return_value.status_code = 200
            mocked_put.return_value.ok = True

            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params, False)

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.json())
