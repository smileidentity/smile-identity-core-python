"""Test class of Utilities"""
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple
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
            0, id_info_params, partner_params,
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
    signature_ = {"signature": signature["signature"], "timestamp": None}  # type: ignore # noqa
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


@responses.activate
def test_validate_id_params_raise_when_given_invalid_input_for_jt6(
    partner_params_jt6: Dict[str, Any],
    client_utilities: Utilities,
    kyc_id_info: Dict[str, str],
) -> None:
    """Validates when wrong input for document verification is provided"""

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
