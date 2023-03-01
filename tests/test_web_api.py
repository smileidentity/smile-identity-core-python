""" Test class for Web API"""
import base64
import os
from datetime import datetime, timedelta
from typing import List, cast
from uuid import uuid4

import pytest
import responses
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from requests import Response

from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.types import ImageParams, OptionsParams, SignatureParams
from smile_id_core.Utilities import Utilities
from smile_id_core.WebApi import WebApi
from tests.stub_mixin import TestCaseWithStubs

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")


class TestWebApi(TestCaseWithStubs):
    """Checks through unittests that all function in Web API application file
    are tested"""

    def setUp(self) -> None:
        """Setups/initialises relevant params for tests and validates them"""
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.api_key = base64.b64encode(self.public_key).decode("UTF-8")
        self.partner_id = "001"
        self.calback_url = "https://a_callback.com"
        self.callback_none = None
        self.sid_server = 0
        self.__reset_params()
        self.web_api = WebApi(
            self.partner_id, self.api_key, "https://a_callback.com", 90
        )
        self.assertEqual(self.web_api.url, "90")
        self.web_api = WebApi("001", "https://a_callback.com", self.api_key, 0)
        self.signature_ = Signature(self.partner_id, self.api_key)
        self.cipher = PKCS1_v1_5.new(cast(RSA.RsaKey, self.key.exportKey()))
        self.assertRaises(
            ValueError,
            WebApi,
            self.partner_id,
            "https://a_callback.com",
            None,
            0,
        )
        self.assertRaises(
            ValueError, WebApi, None, "https://a_callback.com", self.api_key, 0
        )

    def __reset_params(self) -> None:

        self.partner_params = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": JobType.BIOMETRIC_KYC,
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
            "entered": "true",
        }
        self.image_params: List[ImageParams] = []
        with open(image_path, "rb") as binary_file:
            base64_data = base64.b64encode(binary_file.read())
            base64_str = base64_data.decode("utf-8")

        self.image_params.append(
            {
                "image_type_id": 2,
                "image": base64_str,
            }
        )
        self.options_params: OptionsParams = {
            "return_job_status": True,
            "return_history": True,
            "return_images": True,
            "use_enrolled_image": True,
        }

    def test_instance(self) -> None:
        """Performs value checks on partner id, api key, callback url
        and endpoint url"""
        self.__reset_params()
        assert self.web_api.partner_id == "001"
        assert self.web_api.api_key == self.api_key
        assert self.web_api.call_back_url == "https://a_callback.com"
        assert self.web_api.url == "https://testapi.smileidentity.com/v1"

    def test_no_image_params(self) -> None:
        """Checks for when image_params is None"""
        self.__reset_params()
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                None,  # type: ignore
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "Please ensure that you send through image details"
        )

    def test_no_callback_url_jt5(self):
        """callback url is empty and job type is Enhanced KYC"""
        self.__reset_params()
        self.web_api = WebApi(
            self.partner_id, self.calback_url, self.api_key, self.sid_server
        )
        self.partner_params["job_type"] = JobType.ENHANCED_KYC
        self.assertRaises(
            ValueError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            self.id_info_params,
            self.options_params,
            True,
        )

    def test_no_id_info_params_jt5(self) -> None:
        """Checks when All id_info_params values are empty and job type is
        enhanced KYC"""
        self.__reset_params()
        self.partner_params["job_type"] = JobType.ENHANCED_KYC
        self.web_api = WebApi(
            self.partner_id,
            "https://a_callback.com",
            self.api_key,
            self.sid_server,
        )

        self.assertRaises(
            ValueError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            {},
            self.options_params,
            True,
        )

        self.__reset_params()
        self.partner_params["job_type"] = JobType.BIOMETRIC_KYC
        self.web_api = WebApi(
            self.partner_id,
            "https://a_callback.com",
            self.api_key,
            self.sid_server,
        )

        self.assertRaises(
            ServerError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            {},
            self.options_params,
            True,
        )

    def test_no_option_params(self):
        """Validates when no option params is provided(empty or None)"""
        self.__reset_params()
        self.web_api = WebApi(
            self.partner_id, "", self.api_key, self.sid_server
        )
        self.assertRaises(
            ValueError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            self.id_info_params,
            "",
            True,
        )

    def test_validate_return(self):
        """Validates on return data from WebAPi submit_job module call"""
        self.__reset_params()
        self.web_api = WebApi(
            self.partner_id, "", self.api_key, self.sid_server
        )
        self.options_params["return_job_status"] = False
        self.assertRaises(
            ValueError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            self.id_info_params,
            self.options_params,
            False,
        )

    def test__validate_options(self):
        """Performs checks for when option_params return_job_status is
        false"""
        self.__reset_params()
        self.web_api = WebApi(self.partner_id, "calback_url", self.api_key, 0)
        self.options_params["return_job_status"] = False
        self.assertRaises(
            ValueError,
            self.web_api.submit_job,
            self.partner_params,
            self.image_params,
            self.id_info_params,
            self.options_params,
            True,
        )

    def test_no_partner_params(self) -> None:
        """Checks/Handles no partner_params (None)"""
        self.__reset_params()
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                None,  # type: ignore
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "Please ensure that you send through partner params"
        )

    @responses.activate
    def test_success_true_smile_job_type(self) -> None:
        """check return data for valid smile_job_type when option_params
        return_job_status is false"""
        self.__reset_params()
        signature = self._get_signature()
        self.stub_upload_request(signature)
        signature["timestamp"] = (
            datetime.now() - timedelta(days=1)
        ).isoformat()
        self.stub_get_job_status(signature, True)
        self.stub_get_job_status(signature, True, "ERROR MSG")
        self.options_params["return_job_status"] = False

        # TODO: Modify this code; shouldn't be hardcoded
        self.assertEqual(
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            ),
            {"success": True, "smile_job_id": "0000000857"},
        )

    def test_missing_partner_params_for_at_least_1_param(self) -> None:
        """Checks/Handles no partner_params (None)"""
        self.__reset_params()
        self.partner_params["user_id"] = None
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

        self.__reset_params()
        self.partner_params["job_id"] = None
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

        self.__reset_params()
        self.partner_params["job_type"] = None
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

    def test_id_info_params(self):
        """This test raises an error when at least one of the id_info_params
        value is missing. Performs checks for country, id_type, and id_number
        """
        self.__reset_params()
        self.id_info_params["country"] = None  # type: ignore
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert str(value_error.value) == "key country cannot be empty"

        self.__reset_params()
        self.id_info_params["id_number"] = None  # type: ignore
        self.partner_id = ""
        self.partner_params["job_type"] = JobType.BIOMETRIC_KYC
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert str(value_error.value) == "key id_number cannot be empty"

    def test_non_valid_image(self) -> None:
        """Checks for invalid images/non-existent images"""
        self.__reset_params()
        self.image_params.append(
            {
                "image_type_id": 0,
                "file_name": "path/to/image.jpg",
            }
        )
        with pytest.raises(FileNotFoundError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
            )
        assert (
            str(value_error.value)
            == "No such file or directory path/to/image.jpg"
        )

    def test_boolean_options_params_non_jt5(self) -> None:
        """Checks that option_params' return_job_status key is a boolean"""
        self.__reset_params()
        self.options_params["return_job_status"] = "Test"  # type: ignore
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        assert (
            str(value_error.value) == "return_job_status needs to be a boolean"
        )

        self.__reset_params()
        self.options_params["return_history"] = "tEST"  # type: ignore
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        assert str(value_error.value) == "return_history needs to be a boolean"

        self.__reset_params()
        self.options_params["return_images"] = "tEST"  # type: ignore
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        assert str(value_error.value) == "return_images needs to be a boolean"

        self.__reset_params()
        self.options_params["signature"] = "tEST"  # type: ignore
        with pytest.raises(ValueError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        assert str(value_error.value) == "signature needs to be a boolean"

    @responses.activate
    def test_submit_job_should_raise_error_when_pre_upload_fails(self) -> None:
        """Checks if pre_upload fails"""
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
        with pytest.raises(ServerError) as value_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )
        assert (
            str(value_error.value) == "Failed to post entity to"
            " https://testapi.smileidentity.com/v1/upload, status=400,"
            " response={'code': '2204', 'error': 'unauthorized'}"
        )

    @responses.activate
    def test_submit_job_should_raise_error_when_upload_fails(self) -> None:
        """Validation to check if image upload fails"""
        signature = self._get_signature()
        error = "Failed to upload zip"
        post_response = self.stub_upload_request(signature, error)

        self.__reset_params()
        with pytest.raises(ServerError) as server_error:
            self.web_api.submit_job(
                self.partner_params,
                self.image_params,
                self.id_info_params,
                self.options_params,
                False,
            )

        response = {"code": "2205", "error": error}
        assert (
            str(server_error.value)
            == f"Failed to post entity to {post_response['upload_url']},"
            f" status=400, response={response}"
        )

        # Validate for jobtype not equal to 5 (JobType.ENHANCED_KYC)
        utilities = Utilities(self.partner_id, self.api_key, self.sid_server)
        self.assertIsNone(
            utilities.validate_partner_params(self.partner_params)
        )

        self.web_api = WebApi("001", "https://a_callback.com", self.api_key, 0)

    @responses.activate
    def test_validate_return_data(self) -> None:
        """Checks return data validity from web API job submission"""
        self.__reset_params()
        signature = self._get_signature()
        self.stub_upload_request(signature)
        self.stub_get_job_status(signature, False)
        job_status_response = self.stub_get_job_status(signature, True)

        response = self.web_api.submit_job(
            self.partner_params,
            self.image_params,
            self.id_info_params,
            self.options_params,
            False,
        )

        # response = cast(Response, response)
        assert response
        assert response == job_status_response

    @responses.activate
    def test_get_web_token(self) -> None:
        """Creates an authorization token used in Hosted Web Integration"""
        responses.add(
            responses.POST,
            "https://testapi.smileidentity.com/v1/token",
            status=400,
            json={"error": "Invalid product.", "code": "2217"},
        )
        signature = self._get_signature()
        user_id = "user_id"
        job_id = "job_id"
        product = "product_type"
        self.web_api.get_web_token(
            user_id, job_id, product, timestamp=signature["timestamp"]
        )
        body = {
            "timestamp": signature["timestamp"],
            "signature": signature["signature"],
            "user_id": user_id,
            "job_id": job_id,
            "product": product,
            "callback_url": "https://a_callback.com",
            "partner_id": "001",
        }
        self.assert_request_called_with(
            "https://testapi.smileidentity.com/v1/token", responses.POST, body
        )

    def _get_signature(self) -> SignatureParams:
        return self.signature_.generate_signature(
            timestamp=datetime.now().isoformat()
        )

    def test_poll_job_status(self):
        self.__reset_params()
        # Create an instance of the class
        test_obj = WebApi(
            self.partner_id, self.calback_url, self.api_key, self.sid_server
        )

        pytest.raises(
            ServerError,
            test_obj.poll_job_status,
            5,
            self.partner_params,
            self.options_params,
            None,
        )
        assert test_obj.signature_params is not None

        pytest.raises(
            ServerError,
            test_obj.poll_job_status,
            5,
            self.partner_params,
            self.options_params,
            self.signature_.generate_signature(None),
        )
        test_obj.utilities = None
        pytest.raises(
            ValueError,
            test_obj.poll_job_status,
            5,
            self.partner_params,
            self.options_params,
            self.signature_.generate_signature(None),
        )
