"""Test class for ID API"""
from datetime import datetime
from typing import Any, Dict, Tuple
from unittest.mock import patch

import pytest

from smile_id_core import IdApi, ServerError, Signature
from smile_id_core.constants import JobType


def test_handle_wrong_credentials(
    setup_client: Tuple[str, str, str], signature_fixture: Signature
) -> None:
    """Validate keys required for making queries and job submission."""
    api_key, partner_id, _ = setup_client
    assert api_key == signature_fixture.api_key
    id_api = IdApi(partner_id, api_key, 20)
    assert id_api.url == "20"
    id_api = IdApi(partner_id, api_key, 0)
    pytest.raises(ValueError, IdApi, partner_id, None, 0)
    pytest.raises(ValueError, IdApi, None, api_key, 0)


def test_instance(setup_client: Tuple[str, str, str], client: IdApi) -> None:
    """Perform value checks on partner id, api key and endpoint url"""
    api_key, _, _ = setup_client
    assert client.partner_id == "001"
    assert client.api_key == api_key
    assert client.url == "https://testapi.smileidentity.com/v1"


def test_empty_partner_id(setup_client: Tuple[str, str, str]) -> None:
    """Check for empty partner_id and raises an error"""
    api_key, _, _ = setup_client
    with pytest.raises(ValueError) as value_error:
        IdApi("", api_key, 0)
    assert (
        str(value_error.value)
        == "partner_id or api_key cannot be null or empty"
    )


def test_no_partner_params(
    client: IdApi,
    kyc_partner_params: Dict[str, Any],
) -> None:
    """Check for missing partner params and raises an error"""
    id_info_params = kyc_partner_params
    with pytest.raises(ValueError) as value_error:
        client.submit_job({}, id_info_params)
    assert (
        str(value_error.value)
        == "Please ensure that you send through partner params"
    )


def test_no_id_info_params(
    client: IdApi,
    kyc_partner_params: Dict[str, Any],
) -> None:
    """Check for missing id_info_params in ID API calls"""
    partner_params = kyc_partner_params
    with pytest.raises(ValueError) as value_error:
        client.submit_job(partner_params, None)  # type: ignore
    assert (
        str(value_error.value)
        == "Please ensure that you send through ID Information"
    )


def test_invalid_job_type(
    client: IdApi,
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
) -> None:
    """Check for missing job_type in ID API calls"""
    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    partner_params["job_type"] = JobType.BIOMETRIC_KYC
    with pytest.raises(ValueError) as value_error:
        client.submit_job(partner_params, id_info_params, False)
    assert str(value_error.value) == "Job type must be 5 for ID Api"


def test_id_info_params(
    client: IdApi,
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
) -> None:
    """This test raises an error when at least one of the id_info_params
    value is missing. Performs checks for country, id_type, and id_number
    """
    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    id_info_params["country"] = ""
    pytest.raises(
        ValueError,
        client.submit_job,
        partner_params,
        id_info_params,
    )

    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    id_info_params["id_type"] = ""
    pytest.raises(
        ValueError,
        client.submit_job,
        partner_params,
        id_info_params,
    )

    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    id_info_params["id_number"] = ""
    pytest.raises(
        ValueError,
        client.submit_job,
        partner_params,
        id_info_params,
    )


def get_id_response(signature_fixture: Signature) -> Dict[str, Any]:
    """Set up mocked example of expected json response for ID API tests"""
    signature = signature_fixture.generate_signature(
        timestamp=datetime.now().isoformat()
    )
    return {
        "JSONVersion": "1.0.0",
        "SmileJobID": "0000000324",
        "PartnerParams": {
            "job_id": "D7t4PtgWk9kl",
            "user_id": "fffafbdc-073f-44b1-81f5-588866124ae2",
            "job_type": JobType.ENHANCED_KYC,
        },
        "ResultType": "ID Verification",
        "ResultText": "ID Number Validated",
        "ResultCode": "1012",
        "IsFinalResult": "true",
        "Actions": {
            "Verify_ID_Number": "Verified",
            "Return_Personal_Info": "Returned",
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
        "FullData": {},
        "Source": "ID API",
        "timestamp": signature.get("timestamp"),
        "signature": signature.get("signature"),
    }


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
        }
    }


def test_error_return_data(
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    client: IdApi,
) -> None:
    """Tests for error return data due to server error"""
    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    with pytest.raises(ServerError) as value_error:
        with patch("requests.post") as mocked_post, patch(
            "requests.get"
        ) as mocked_get:
            mocked_post.return_value.status_code = 400
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }
            mocked_post.return_value.json.return_value = {
                "code": "2204",
                "error": "unauthorized",
            }

            mocked_get.return_value.status_code = 200
            mocked_get.return_value.ok = True
            mocked_get.return_value.text.return_value = (
                get_smile_services_response()
            )
            mocked_get.return_value.json.return_value = (
                get_smile_services_response()
            )

            client.submit_job(partner_params, id_info_params)
    assert (
        str(value_error.value) == "Failed to post entity to "
        "https://testapi.smileidentity.com/v1/id_verification, status=400,"
        " response={'code': '2204', 'error': 'unauthorized'}"
    )


def test_validate_return_data(
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    signature_fixture: Signature,
    client: IdApi,
) -> None:
    """Uses mocked examples for payload responses; checks that
    response status code is 200 and response body is not empty"""
    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.ok = True
        mocked_post.return_value.text.return_value = get_id_response(
            signature_fixture,
        )
        mocked_post.return_value.json.return_value = get_id_response(
            signature_fixture,
        )

        response = client.submit_job(partner_params, id_info_params, False)

        assert response is not None

        assert (
            response["PartnerParams"]
            == get_id_response(signature_fixture)["PartnerParams"]
        )

        assert (
            response["IDNumber"]
            == get_id_response(signature_fixture)["IDNumber"]
        )


def test_validate_return_data_business_verification(
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    signature_fixture: Signature,
    client: IdApi,
) -> None:
    """Uses mocked examples for payload responses; checks that
    response status code is 200 and response body is not empty"""

    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    signature_fixture.generate_signature()
    partner_params["job_type"] = JobType.BUSINESS_VERIFICATION
    id_info_params = {
        "country": "NG",
        "id_type": "BUSINESS_REGISTRATION",
        "id_number": "0000000",
        "business_type": "co",
        "partner_id": "001",
    }

    with patch("requests.post") as mocked_post:
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.ok = True
        mocked_post.return_value.text.return_value = (
            get_id_response(signature_fixture),
        )
        mocked_post.return_value.json.return_value = get_id_response(
            signature_fixture,
        )

        response = client.submit_job(partner_params, id_info_params, False)

        assert response


def test_custom_sid_server_url(setup_client: Tuple[str, str, str]) -> None:
    """Checks for custom server url"""
    api_key, _, _ = setup_client
    custom_url: str = "https://custom-url.com"
    id_api = IdApi("001", api_key, custom_url)
    assert id_api.url == custom_url
