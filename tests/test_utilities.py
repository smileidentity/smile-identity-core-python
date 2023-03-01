"""Test class of Utilities"""
import base64
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Union, cast
from unittest.mock import patch
from uuid import uuid4

import pytest
import responses
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.types import OptionsParams
from smile_id_core.Utilities import (
    Utilities,
    get_signature,
    get_version,
    validate_signature_params,
)
from tests.stub_mixin import TestCaseWithStubs


class TestUtilities(TestCaseWithStubs):
    """Sets up useful variables for validation/checks"""

    def test_get_version(self) -> None:
        """Test that a well formatted version string is returned."""
        version = get_version()
        assert isinstance(version, str)
        # tests that the version is in the form of a semver string.
        assert re.match(r"^\d+\.\d+\.\d+$", version)

    def setUp(self) -> None:
        """Setups/initialises relevant params for tests and validates them"""
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.api_key = base64.b64encode(self.public_key).decode("UTF-8")
        self.partner_id = "001"
        self.signature_ = Signature(self.partner_id, self.api_key)
        self.cipher = PKCS1_v1_5.new(cast(RSA.RsaKey, self.key.exportKey()))
        self.__reset_params()
        self.utilities = Utilities(self.partner_id, self.api_key, 90)
        assert self.utilities.url == "90"
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        pytest.raises(ValueError, Utilities, self.partner_id, None, 0)
        pytest.raises(ValueError, Utilities, None, self.api_key, 0)

    def __reset_params(self) -> None:
        self.partner_params = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": JobType.BIOMETRIC_KYC,
        }

        self.partner_params_jt6 = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": JobType.DOCUMENT_VERIFICATION,
        }

        self.id_info_params: Dict[str, str] = {
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
        self.image_params = []
        self.image_params.append(
            {
                "image_type_id": 2,
                "image": "base64image",
                "file_name": "",
            }
        )
        self.options_params = OptionsParams(
            return_job_status=True,
            return_history=True,
            return_images=True,
            use_enrolled_image=False,
        )

    def test_instance(self) -> None:
        """Performs value checks on partner id, api key and endpoint url"""
        assert self.utilities.partner_id == "001"
        assert self.utilities.api_key == self.api_key
        assert self.utilities.url == "https://testapi.smileidentity.com/v1"

    @staticmethod
    def _get_smile_services_response() -> Dict[str, Any]:
        """Returns supported Nigeria ID type examples for mocks"""
        return {
            "id_types": {
                "NG": {
                    "NIN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                    ],
                    "CAC": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "company",
                        "job_id",
                    ],
                    "TIN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                    ],
                    "VOTER_ID": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                    ],
                    "BVN": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                    ],
                    "PHONE_NUMBER": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                    ],
                    "DRIVERS_LICENSE": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob",
                    ],
                    "PASSPORT": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob",
                    ],
                },
            },
            "hosted_web": {
                "doc_verification": {
                    "NG": {
                        "name": "Nigeria",
                        "id_types": {
                            "VOTER_ID": {"label": "Voter's ID"},
                            "NIN": {"label": "National ID"},
                            "PASSPORT": {"label": "Passport"},
                            "DRIVERS_LICENSE": {"label": "Driver's License"},
                        },
                    }
                },
            },
        }

    def test_validate_id_params(self) -> None:
        """Test to validate when fields of id_info_params is empty and
        entered is None"""
        self.__reset_params()
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        id_info_params = {
            "first_name": "",
            "last_name": "",
            "country": "",
            "id_type": "",
            "id_number": "",
            "dob": "",
            "entered": None,
        }

        partner_params = {
            "job_id": f"job-{uuid.uuid4()}",
            "user_id": f"user-{uuid.uuid4()}",
            "job_type": JobType.BUSINESS_VERIFICATION,
        }

        self.utilities = Utilities(self.partner_id, self.api_key, 0)

        assert (
            Utilities.validate_id_params(
                0, id_info_params, partner_params, use_validation_api=False
            )
            is None
        )

        # No country provided for test
        id_info_params = {
            "first_name": "",
            "last_name": "",
            "id_type": "",
            "id_number": "",
            "dob": "",
            "entered": "true",
        }

        pytest.raises(
            ValueError,
            Utilities.validate_id_params,
            0,
            id_info_params,
            partner_params,
            use_validation_api=False,
        )

        self.__reset_params()

        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        self.partner_params["job_type"] = JobType.DOCUMENT_VERIFICATION
        signature = self.signature_.generate_signature(
            datetime.now().isoformat()
        )
        signature["timestamp"] = (
            datetime.now() - timedelta(days=1)
        ).isoformat()
        self.stub_get_job_status(signature, True, None)
        self.utilities = Utilities(self.partner_id, self.api_key, 0)

    def test_validate_signature_params(self) -> None:
        """Validates signature params"""
        signature = self.signature_.generate_signature(
            datetime.now().isoformat()
        )
        signature_ = {"timestamp": signature["timestamp"]}
        pytest.raises(Exception, validate_signature_params, signature_)
        signature_ = {"signature": signature["signature"], "timestamp": None}  # type: ignore
        pytest.raises(Exception, validate_signature_params, signature_)

    def test_no_partner_params(self) -> None:
        """Checks for missing partner params and raises an error"""
        self.__reset_params()
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_partner_params(None)  # type: ignore
        assert (
            str(value_error.value)
            == "Please ensure that you send through partner params"
        )

    def test_missing_partner_params(self) -> None:
        """Validation for missing partner params (partner_params = None)"""
        self.__reset_params()
        self.partner_params["user_id"] = None
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_partner_params(self.partner_params)
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

        self.__reset_params()
        self.partner_params["job_id"] = None
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_partner_params(self.partner_params)
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

        self.__reset_params()
        self.partner_params["job_type"] = None
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_partner_params(self.partner_params)
        assert (
            str(value_error.value)
            == "Partner Parameter Arguments may not be null or empty"
        )

        partner_params: Dict[str, Any] = {
            "user_id": 100,
            "job_id": str(uuid4()),
            "job_type": JobType.BIOMETRIC_KYC,
        }
        pytest.raises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        partner_params["user_id"] = str(uuid.uuid1)
        partner_params["job_id"] = 56
        pytest.raises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )
        partner_params["job_id"] = str(uuid4())
        partner_params["job_type"] = str(uuid.uuid4())

        pytest.raises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )
        self.assertRaises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        partner_params["user_id"] = str(uuid.uuid1)
        partner_params["job_id"] = 56
        self.assertRaises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )
        partner_params["job_id"] = str(uuid4())
        partner_params["job_type"] = str(uuid.uuid4())

        self.assertRaises(
            ValueError, self.utilities.validate_partner_params, partner_params
        )

    @responses.activate
    def test_validate_id_params_should_raise_when_provided_with_invalid_input(
        self,
    ) -> None:
        """Validate id parameters using the smile services endpoint which
        checks the provided id params, and partner params"""
        self.__reset_params()

        self._stub_service("https://testapi.smileidentity.com/v1")
        self.id_info_params["country"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
            )
        assert str(value_error.value) == "key country cannot be empty"

        self.__reset_params()
        self.id_info_params["id_type"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
            )
        assert str(value_error.value) == "key id_type cannot be empty"

        self.__reset_params()
        self.id_info_params["id_number"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
            )
        assert str(value_error.value) == "key id_number cannot be empty"

        self.__reset_params()
        self.id_info_params["country"] = "ZW"
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
                use_validation_api=True,
            )
        assert str(value_error.value) == "country ZW is invalid"

        self.__reset_params()
        self.id_info_params["id_type"] = "Not_Supported"
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
                use_validation_api=True,
            )
        assert str(value_error.value) == "id_type Not_Supported is invalid"

        self.__reset_params()
        self.partner_params["user_id"] = None
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
                use_validation_api=True,
            )
        assert str(value_error.value) == "key user_id cannot be empty"

        self.__reset_params()
        self.id_info_params["first_name"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params,
                use_validation_api=True,
            )
        assert str(value_error.value) == "key first_name cannot be empty"

        self.__reset_params()
        # self.partner_params.pop(self.partner_params.get("user_id"))
        updated_partner_params = dict(self.partner_params)
        del updated_partner_params["user_id"]
        print(self.partner_params)
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                updated_partner_params,
                use_validation_api=True,
            )
        assert str(value_error.value) == "key user_id is required"

    @responses.activate
    def test_validate_id_params_raise_when_given_invalid_input_for_jt6(
        self,
    ) -> None:
        """Validates when wrong input for document verification is provided"""
        self.__reset_params()
        self._stub_service("https://testapi.smileidentity.com/v1")
        self.id_info_params["country"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params_jt6,
            )
        assert str(value_error.value) == "key country cannot be empty"

        self.__reset_params()
        self.id_info_params["id_type"] = ""
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params_jt6,
            )
        assert str(value_error.value) == "key id_type cannot be empty"

        self.__reset_params()
        self.id_info_params["id_number"] = ""

        self.__reset_params()
        self.id_info_params["country"] = "ZW"
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params_jt6,
                use_validation_api=True,
            )
        assert str(value_error.value) == "country ZW is invalid"

        self.__reset_params()
        self.id_info_params["id_type"] = "Not_Supported"
        with pytest.raises(ValueError) as value_error:
            Utilities.validate_id_params(
                self.utilities.url,
                self.id_info_params,
                self.partner_params_jt6,
                use_validation_api=True,
            )
        assert str(value_error.value) == "id_type Not_Supported is invalid"

    @responses.activate
    def test_get_job_status(self) -> None:
        """Tests the stub_get_job_status stub module"""
        self.__reset_params()
        signature = self.signature_.generate_signature(
            datetime.now().isoformat()
        )
        self.stub_get_job_status(signature, True)
        job_status = self.utilities.get_job_status(
            self.partner_params, self.options_params, signature
        )
        body = {
            "signature": signature["signature"],
            "timestamp": signature["timestamp"],
            "partner_id": "001",
            "job_id": self.partner_params["job_id"],
            "user_id": self.partner_params["user_id"],
            "image_links": True,
            "history": True,
        }

        assert job_status.status_code == 200
        assert job_status.json() is not None
        self.assert_request_called_with(
            "https://testapi.smileidentity.com/v1/job_status",
            responses.POST,
            body,
        )

        # Validation for options equals None
        options = OptionsParams(
            return_job_status=True,
            return_history=False,
            return_images=False,
            use_enrolled_image=False,
        )
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        none_option_param = self.utilities.get_job_status(
            self.partner_params, None, signature  # type: ignore
        )
        set_option_param = self.utilities.get_job_status(
            self.partner_params, options, signature
        )
        assert none_option_param.status_code == set_option_param.status_code

        # Check for signature equals None
        self.utilities = Utilities(self.partner_id, self.api_key, 0)
        signature = get_signature(self.partner_id, self.api_key)
        none_signature = self.utilities.get_job_status(
            self.partner_params, options, None
        )
        set_signature = self.utilities.get_job_status(
            self.partner_params, options, signature
        )
        assert none_signature.status_code == set_signature.status_code

    @responses.activate
    def test_get_job_status_raises_server_error(self) -> None:
        """Checks and raises server error when wrong signature value is passed
        to stub_get_job_status"""
        self.__reset_params()
        signature = self.signature_.generate_signature(
            datetime.now().isoformat()
        )
        signature["timestamp"] = (
            datetime.now() - timedelta(days=1)
        ).isoformat()
        self.stub_get_job_status(signature, True, None)

        pytest.raises(
            ServerError,
            self.utilities.get_job_status,
            self.partner_params,
            self.options_params,
            signature,
        )

        signature = self.signature_.generate_signature(
            datetime.now().isoformat()
        )
        self.stub_get_job_status(signature, True, "ERROR MESSAGE")

        pytest.raises(
            ServerError,
            self.utilities.get_job_status,
            self.partner_params,
            self.options_params,
            signature,
        )

    @responses.activate
    def test_get_smile_id_services(self) -> None:
        """Validates job status code after making test api calls to production
        and sandbox through the services_stub_services"""
        self.__reset_params()

        self._stub_service("https://testapi.smileidentity.com/v1")
        self.utilities.get_smile_id_services(0)

        self._stub_service("https://api.smileidentity.com/v1")
        self.utilities.get_smile_id_services(1)

        self._stub_service("https://random-server.smileidentity.com/v1")
        job_status = self.utilities.get_smile_id_services(
            "https://random-server.smileidentity.com/v1"
        )

        assert job_status.status_code == 200

    def test_get_smile_id_services_success(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }

            response = Utilities.get_smile_id_services(0)
            assert response.status_code == 200

    def test_get_smile_id_services_failure(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            mock_get.return_value.json.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }

            pytest.raises(ServerError, Utilities.get_smile_id_services, 0)

    def _stub_service(
        self, url: str, json: Union[Dict[str, Any], Any] = None
    ) -> None:
        """When response from _get_smile_services_response module call is not
        json"""

        if not json:
            json = TestUtilities._get_smile_services_response()

        responses.add(
            responses.GET,
            f"{url}/services",
            json=json,
        )

    def test_error_return_data(self):
        """Tests for error return data due to server error"""
        self.__reset_params()
        with patch("requests.post") as mocked_post, patch(
            "requests.get"
        ) as mocked_get:
            mocked_post.return_value.status_code = 500
            mocked_post.return_value.ok = True
            mocked_post.return_value.text = "Unauthorized"
            mocked_post.return_value.json.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }
            mocked_get.return_value.text = "Unauthorized"
            mocked_get.return_value.json.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }

            with self.assertRaises(ServerError):
                self.utilities.get_smile_id_services(0)
