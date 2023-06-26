"""Test class of Utilities"""
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple, Union
from unittest.mock import patch
from uuid import uuid4

import pytest
import responses

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
from tests.conftest import assert_request_called_with, stub_get_job_status

def test_get_version() -> None:
    """Test that a well formatted version string is returned."""
    version = get_version()
    assert isinstance(version, str)
    # tests that the version is in the form of a semver string.
    assert re.match(r"^\d+\.\d+\.\d+$", version)

def test_handle_wrong_credentials(
    setup_client: Tuple[str, str, str], client_utilities: Utilities
) -> None:
    """Setups/initialises relevant params for tests and validates them"""
    api_key, partner_id, sid_server = setup_client
    sid_server = "90"
    client_utilities = Utilities(partner_id, api_key, sid_server)
    assert client_utilities.url == sid_server
    client_utilities = Utilities(partner_id, api_key, 0)
    pytest.raises(ValueError, Utilities, partner_id, None, 0)
    pytest.raises(ValueError, Utilities, None, api_key, 0)

def test_instance(
    client_utilities: Utilities, setup_client: Tuple[str, str, str]
) -> None:
    """Performs value checks on partner id, api key and endpoint url"""
    api_key, partner_id, _ = setup_client
    assert client_utilities.partner_id == partner_id
    assert client_utilities.api_key == api_key
    assert client_utilities.url == "https://testapi.smileidentity.com/v1"

def get_smile_services_response() -> Dict[str, Any]:
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

def test_validate_id_params(
    setup_client: Tuple[str, str, str], signature_fixture: Signature
) -> None:
    """Test to validate when fields of id_info_params is empty and
    entered is None"""
    api_key, partner_id, _ = setup_client
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

    utilities = Utilities(partner_id, api_key, 0)

    assert (
        utilities.validate_id_params(
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

    utilities = Utilities(partner_id, api_key, 0)
    partner_params["job_type"] = JobType.DOCUMENT_VERIFICATION
    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    signature["timestamp"] = (datetime.now() - timedelta(days=1)).isoformat()
    utilities = Utilities(partner_id, api_key, 0)

def test_validate_signature_params(signature_fixture: Signature) -> None:
    """Validates signature params"""
    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    signature_ = {"timestamp": signature["timestamp"]}
    pytest.raises(Exception, validate_signature_params, signature_)
    signature_ = {"signature": signature["signature"], "timestamp": None}  # type: ignore
    pytest.raises(Exception, validate_signature_params, signature_)

def test_no_partner_params(client_utilities: Utilities) -> None:
    """Checks for missing partner params and raises an error"""

    with pytest.raises(ValueError) as value_error:
        client_utilities.validate_partner_params(None)  # type: ignore
    assert (
        str(value_error.value)
        == "Please ensure that you send through partner params"
    )

def test_missing_partner_params(
    kyc_partner_params: Dict[str, Any], setup_client: Tuple[str, str, str]
) -> None:
    """Validation for missing partner params (partner_params = None)"""
    api_key, partner_id, _ = setup_client
    kyc_partner_params["user_id"] = None
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_partner_params(kyc_partner_params)
    assert (
        str(value_error.value)
        == "Partner Parameter Arguments may not be null or empty"
    )

    kyc_partner_params["job_id"] = None
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_partner_params(kyc_partner_params)
    assert (
        str(value_error.value)
        == "Partner Parameter Arguments may not be null or empty"
    )

    kyc_partner_params["job_type"] = None
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_partner_params(kyc_partner_params)
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
        ValueError,
        Utilities.validate_partner_params,
        partner_params,
    )
    utilities = Utilities(partner_id, api_key, 0)
    partner_params["user_id"] = str(uuid.uuid1)
    partner_params["job_id"] = 56
    pytest.raises(
        ValueError,
        utilities.validate_partner_params,
        partner_params,
    )
    partner_params["job_id"] = str(uuid4())
    partner_params["job_type"] = str(uuid.uuid4())

    pytest.raises(
        ValueError,
        utilities.validate_partner_params,
        partner_params,
    )
    pytest.raises(
        ValueError,
        utilities.validate_partner_params,
        partner_params,
    )
    utilities = Utilities(partner_id, api_key, 0)
    partner_params["user_id"] = str(uuid.uuid1)
    partner_params["job_id"] = 56
    pytest.raises(
        ValueError,
        utilities.validate_partner_params,
        partner_params,
    )
    partner_params["job_id"] = str(uuid4())
    partner_params["job_type"] = str(uuid.uuid4())

    pytest.raises(
        ValueError,
        utilities.validate_partner_params,
        partner_params,
    )

@responses.activate
def test_validate_id_params_should_raise_when_provided_with_invalid_input(
    kyc_id_info: Dict[str, str],
    kyc_partner_params: Dict[str, Any],
    client_utilities: Utilities,
) -> None:
    """Validate id parameters using the smile services endpoint which
    checks the provided id params, and partner params"""

    stub_service("https://testapi.smileidentity.com/v1")
    kyc_id_info["country"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
        )
    assert str(value_error.value) == "key country cannot be empty"
    kyc_id_info["country"] = "NG"
    kyc_id_info["id_type"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
        )
    assert str(value_error.value) == "key id_type cannot be empty"
    kyc_id_info["id_type"] = "PASSPORT"
    kyc_id_info["id_number"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
        )
    assert str(value_error.value) == "key id_number cannot be empty"
    kyc_id_info["id_number"] = "A00000000"
    kyc_id_info["country"] = "ZW"
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
            use_validation_api=True,
        )
    assert str(value_error.value) == "country ZW is invalid"

    kyc_id_info["country"] = "NG"
    kyc_id_info["id_type"] = "Not_Supported"
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
            use_validation_api=True,
        )
    assert str(value_error.value) == "id_type Not_Supported is invalid"
    kyc_id_info["id_type"] = "PASSPORT"
    kyc_partner_params["user_id"] = None
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
            use_validation_api=True,
        )
    assert str(value_error.value) == "key user_id cannot be empty"

    kyc_partner_params["user_id"] = "kyb_test_user_008"
    kyc_id_info["first_name"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            kyc_partner_params,
            use_validation_api=True,
        )
    assert str(value_error.value) == "key first_name cannot be empty"
    kyc_id_info["first_name"] = "FirstName"
    updated_partner_params = dict(kyc_partner_params)
    del updated_partner_params["user_id"]
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            updated_partner_params,
            use_validation_api=True,
        )
    assert str(value_error.value) == "key user_id is required"

@responses.activate
def test_validate_id_params_raise_when_given_invalid_input_for_jt6(
    partner_params_jt6: Dict[str, Any],
    client_utilities: Utilities,
    kyc_id_info: Dict[str, str],
) -> None:
    """Validates when wrong input for document verification is provided"""

    stub_service("https://testapi.smileidentity.com/v1")
    kyc_id_info["country"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            partner_params_jt6,
        )
    assert str(value_error.value) == "key country cannot be empty"
    kyc_id_info["country"] = "NG"
    kyc_id_info["id_type"] = ""
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            partner_params_jt6,
        )
    assert str(value_error.value) == "key id_type cannot be empty"

    kyc_id_info["id_type"] = "PASSPORT"
    kyc_id_info["country"] = "ZW"
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            partner_params_jt6,
            use_validation_api=True,
        )
    assert str(value_error.value) == "country ZW is invalid"

    kyc_id_info["country"] = "NG"
    kyc_id_info["id_type"] = "Not_Supported"
    with pytest.raises(ValueError) as value_error:
        Utilities.validate_id_params(
            client_utilities.url,
            kyc_id_info,
            partner_params_jt6,
            use_validation_api=True,
        )
    assert str(value_error.value) == "id_type Not_Supported is invalid"

@responses.activate
def test_get_job_status(
    signature_fixture: Signature,
    client_utilities: Utilities,
    option_params: OptionsParams,
    kyc_partner_params: Dict[str, Any],
    setup_client: Tuple[str, str, str],
) -> None:
    """Tests the stub_get_job_status stub module"""

    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    stub_get_job_status(signature, True)
    job_status = client_utilities.get_job_status(
        kyc_partner_params, option_params, signature
    )
    api_key, partner_id, _ = setup_client

    body = {
        "signature": signature["signature"],
        "timestamp": signature["timestamp"],
        "partner_id": "001",
        "job_id": kyc_partner_params["job_id"],
        "user_id": kyc_partner_params["user_id"],
        "image_links": True,
        "history": True,
    }

    assert job_status.status_code == 200
    assert job_status.json() is not None
    assert_request_called_with(
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
    none_option_param = client_utilities.get_job_status(
        kyc_partner_params, None, signature  # type: ignore
    )
    set_option_param = client_utilities.get_job_status(
        kyc_partner_params, options, signature
    )
    assert none_option_param.status_code == set_option_param.status_code

    # Check for signature equals None
    signature = get_signature(partner_id, api_key)
    none_signature = client_utilities.get_job_status(
        kyc_partner_params, options, None
    )
    set_signature = client_utilities.get_job_status(
        kyc_partner_params, options, signature
    )
    assert none_signature.status_code == set_signature.status_code

@responses.activate
def test_get_job_status_raises_server_error(
    signature_fixture: Signature,
    client_utilities: Utilities,
    kyc_partner_params: Dict[str, Any],
    option_params: OptionsParams,
) -> None:
    """Checks and raises server error when wrong signature value is passed
    to stub_get_job_status"""

    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    signature["timestamp"] = (datetime.now() - timedelta(days=1)).isoformat()
    stub_get_job_status(signature, True, None)

    pytest.raises(
        ServerError,
        client_utilities.get_job_status,
        kyc_partner_params,
        option_params,
        signature,
    )

    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    stub_get_job_status(signature, True, "ERROR MESSAGE")

    pytest.raises(
        ServerError,
        client_utilities.get_job_status,
        kyc_partner_params,
        option_params,
        signature,
    )

@responses.activate
def test_get_smile_id_services(client_utilities: Utilities) -> None:
    """Validates job status code after making test api calls to production
    and sandbox through the servicesstub_services"""

    stub_service("https://testapi.smileidentity.com/v1")
    client_utilities.get_smile_id_services(0)

    stub_service("https://api.smileidentity.com/v1")
    client_utilities.get_smile_id_services(1)

    stub_service("https://random-server.smileidentity.com/v1")
    job_status = client_utilities.get_smile_id_services(
        "https://random-server.smileidentity.com/v1"
    )

    assert job_status.status_code == 200

def test_get_smile_id_services_success():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "code": "2204",
            "error": "unauthorized",
        }

        response = Utilities.get_smile_id_services(0)
        assert response.status_code == 200

def test_get_smile_id_services_failure():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {
            "code": "2204",
            "error": "unauthorized",
        }

        pytest.raises(ServerError, Utilities.get_smile_id_services, 0)

def stub_service(url: str, json: Union[Dict[str, Any], Any] = None) -> None:
    """When response from get_smile_services_response module call is not
    json"""

    if not json:
        json = get_smile_services_response()

    responses.add(
        responses.GET,
        f"{url}/services",
        json=json,
    )

def test_error_return_data(client_utilities):
    """Tests for error return data due to server error"""

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

        with pytest.raises(ServerError):
            client_utilities.get_smile_id_services(0)
