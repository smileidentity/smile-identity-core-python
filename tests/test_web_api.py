import base64
import time
from datetime import datetime
from typing import Dict
from uuid import uuid4

import responses
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core import WebApi, Signature, ServerError
from tests.stub_mixin import TestCaseWithStubs


class TestWebApi(TestCaseWithStubs):
    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.api_key = base64.b64encode(self.public_key).decode("UTF-8")
        self.partner_id = "001"
        self.__reset_params()
        self.web_api = WebApi("001", "https://a_callback.com", self.api_key, 0)
        self.signatureObj = Signature(self.partner_id, self.api_key)
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
        self.assertEqual(self.web_api.api_key, self.api_key)
        self.assertEqual(self.web_api.call_back_url, "https://a_callback.com")
        self.assertEqual(
            self.web_api.url,
            "https://testapi.smileidentity.com/v1",
        )

    def test_no_image_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params, None, self.id_info_params, self.options_params
            )
        self.assertEqual(
            ve.exception.args[0], "Please ensure that you send through image details"
        )

    def test_no_partner_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                None, self.image_params, self.id_info_params, self.options_params
            )
        self.assertEqual(
            ve.exception.args[0], "Please ensure that you send through partner params"
        )

    def test_missing_partner_params(self):
        self.__reset_params()
        self.partner_params["user_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        value_exception = ve.exception
        self.assertEqual(
            value_exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

        self.__reset_params()
        self.partner_params["job_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(
            ve.exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

        self.__reset_params()
        self.partner_params["job_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(
            ve.exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

    def test_id_info_params(self):
        self.__reset_params()
        self.id_info_params["country"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(ve.exception.args[0], "key country cannot be empty")

        self.__reset_params()
        self.id_info_params["id_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(ve.exception.args[0], "key id_type cannot be empty")

        self.__reset_params()
        self.id_info_params["id_number"] = None
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(ve.exception.args[0], "key id_number cannot be empty")

    def test_non_valid_image(self):
        self.__reset_params()
        self.image_params.append({"image_type_id": "0", "image": "path/to/image.jpg"})
        with self.assertRaises(FileNotFoundError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        self.assertEqual(
            ve.exception.args[0], "No such file or directory path/to/image.jpg"
        )

    def test_boolean_options_params_non_jt5(self):
        self.__reset_params()
        self.options_params["return_job_status"] = "Test"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        self.assertEqual(
            ve.exception.args[0], "return_job_status needs to be a boolean"
        )

        self.__reset_params()
        self.options_params["return_history"] = "tEST"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        self.assertEqual(ve.exception.args[0], "return_history needs to be a boolean")

        self.__reset_params()
        self.options_params["return_images"] = "tEST"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        self.assertEqual(ve.exception.args[0], "return_images needs to be a boolean")

        self.__reset_params()
        self.options_params["signature"] = "tEST"
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        self.assertEqual(ve.exception.args[0], "signature needs to be a boolean")

    @responses.activate
    def test_submit_job_should_raise_error_when_pre_upload_fails(self):
        responses.add(
            responses.POST,
            "https://testapi.smileidentity.com/v1/upload",
            status=400,
            json={
                "code": "2204",
                "error": "unauthorized",
            },
        )
        self.__reset_params()
        with self.assertRaises(ServerError) as ve:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        self.assertEqual(
            ve.exception.args[0],
            "Failed to post entity to https://testapi.smileidentity.com/v1/upload, status=400, response={'code': '2204', 'error': 'unauthorized'}",
        )

    @responses.activate
    def test_submit_job_should_raise_error_when_upload_fails(self):
        sec_key = self._get_sec_key(False)
        error = "Failed to upload zip"
        post_response = self.stub_upload_request(sec_key, error)

        self.__reset_params()
        with self.assertRaises(ServerError) as ve:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )

        response = {"code": "2205", "error": error}
        self.assertEqual(
            ve.exception.args[0],
            f"Failed to post entity to {post_response['upload_url']}, status=400, response={response}",
        )

    @responses.activate
    def test_validate_return_data(self):
        self.__reset_params()
        sec_key = self._get_sec_key(False)
        post_response = self.stub_upload_request(sec_key)
        self.stub_get_job_status(sec_key, False)
        job_status_response = self.stub_get_job_status(sec_key, True)

        response = self.web_api.submit_job(
            self.partner_params,
            self.image_params,
            self.id_info_params,
            self.options_params,
            False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), job_status_response)

    @responses.activate
    def test_get_web_token(self):
        responses.add(
            responses.POST,
            "https://testapi.smileidentity.com/v1/token",
            status=400,
            json={"error": "Invalid product.", "code": "2217"},
        )
        sec = self._get_sec_key(True)
        user_id = "user_id"
        job_id = "job_id"
        product = "product_type"
        self.web_api.get_web_token(user_id, job_id, product, timestamp=sec["timestamp"])
        body = {
            **sec,
            "user_id": user_id,
            "job_id": job_id,
            "product": product,
            "callback_url": "https://a_callback.com",
            "partner_id": "001",
        }
        self.assert_request_called_with(
            "https://testapi.smileidentity.com/v1/token", responses.POST, body
        )

    def _get_sec_key(self, signature):
        if signature:
            sec_key = self.signatureObj.generate_signature(
                timestamp=datetime.now().isoformat()
            )
        else:
            sec_key = self.signatureObj.generate_sec_key(timestamp=int(time.time()))
        return sec_key
