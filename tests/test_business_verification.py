"""Test class for Business Verification"""
from datetime import datetime
from typing import Any, Dict, Tuple
from unittest.mock import patch

import pytest

from smile_id_core import JobType, ServerError
from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.Signature import Signature

def test_instance(
    setup_client: Tuple[str, str, str], client_kyb: BusinessVerification
) -> None:
    """Perform value checks on partner id, api key and endpoint url"""
    api_key, _, _ = setup_client
    assert client_kyb.partner_id == "001"
    assert client_kyb.api_key == api_key
    assert client_kyb.url == "https://testapi.smileidentity.com/v1"

def test_empty_partner_id(setup_client: Tuple[str, str, str]) -> None:
    """Check for empty partner_id and raises an error"""
    api_key, _, _ = setup_client
    with pytest.raises(ValueError) as value_error:
        BusinessVerification("", api_key, 0)
    assert (
        str(value_error.value)
        == "partner_id or api_key cannot be null or empty"
    )

def test_no_partner_params(
    client_kyb: BusinessVerification,
    kyc_id_info: Dict[str, str],
) -> None:
    """Check for missing partner params and raises an error"""
    with pytest.raises(ValueError) as value_error:
        client_kyb.submit_job({}, kyc_id_info)
    assert (
        str(value_error.value)
        == "Please ensure that you send through partner params"
    )

def test_no_id_info_params(
    client_kyb: BusinessVerification,
    kyc_partner_params: Dict[str, Any],
) -> None:
    """Check for missing id_info_params in ID API calls"""
    with pytest.raises(ValueError) as value_error:
        client_kyb.submit_job(kyc_partner_params, None)  # type: ignore
    assert (
        str(value_error.value)
        == "Please ensure that you send through ID Information"
    )

def test_id_info_params(
    client_kyb: BusinessVerification,
    kyc_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
) -> None:
    """This test raises an error when at least one of the id_info_params
    value is missing. Performs checks for country, id_type, and id_number
    """
    # partner_params, id_info_params = reset_params
    kyc_id_info["country"] = ""
    pytest.raises(
        ValueError,
        client_kyb.submit_job,
        kyc_partner_params,
        kyc_id_info,
    )

    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    id_info_params["id_type"] = ""
    pytest.raises(
        ValueError,
        client_kyb.submit_job,
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
        client_kyb.submit_job,
        partner_params,
        id_info_params,
    )

def test_invalid_job_type(
    client_kyb: BusinessVerification,
    kyc_id_info: Dict[str, str],
    kyc_partner_params: Dict[str, Any],
) -> None:
    """Check for missing job_type in ID API calls"""
    partner_params, id_info_params = (
        kyc_partner_params,
        kyc_id_info,
    )
    partner_params["job_type"] = JobType.BIOMETRIC_KYC
    with pytest.raises(ValueError) as value_error:
        client_kyb.submit_job(partner_params, id_info_params)
    assert str(value_error.value) == "Job type must be 7 for kyb"

def get_id_response(signature_fixture: Signature) -> Dict[str, Any]:
    """Generates Signature and returns a test payload response"""
    signature = signature_fixture.generate_signature(
        timestamp=datetime.now().isoformat()
    )

    return {
        "timestamp": signature.get("timestamp"),
        "signature": signature.get("signature"),
        "JSONVersion": "1.0.0",
        "SmileJobID": "0000001927",
        "PartnerParams": {
            "user_id": "kyb_test_user_008",
            "job_id": "job_id_001",
            "job_type": 7,
        },
        "ResultType": "Business Verification",
        "ResultText": "Business Verified",
        "ResultCode": "1012",
        "IsFinalResult": "true",
        "Actions": {
            "Verify_Business": "Verified",
            "Return_Business_Info": "Returned",
        },
        "company_information": {
            "company_type": "PRIVATE_COMPANY_LIMITED_BY_SHARES",
            "country": "Nigeria",
            "address": "678, Victoria Island, Lagos",
            "registration_number": "0000000",
            "search_number": "0000000",
            "authorized_shared_capital": "10000000",
            "industry": "Technology Solutions Company",
            "tax_id": "N/A",
            "registration_date": "2016-01-28T16:06:22.003+00:00",
            "phone": "08000000000",
            "legal_name": "SMILE IDENTITY NIGERIA LIMITED",
            "state": "LAGOS",
            "email": "smile@smileidentity.com",
            "status": "ACTIVE",
        },
        "fiduciaries": [
            {
                "name": "Company X",
                "fiduciary_type": "SECRETARY_COMPANY",
                "address": "678, Victoria Island, Lagos",
                "registration_number": "000000",
                "status": "N/A",
            }
        ],
        "beneficial_owners": [
            {
                "shareholdings": "100000",
                "address": "678, Victoria Island, Lagos",
                "gender": "Male",
                "nationality": "Nigerian",
                "registration_number": "N/A",
                "name": "Joe Bloggs",
                "shareholder_type": "Individual",
                "phone_number": "0123456789",
            },
            {
                "shareholdings": "700000",
                "address": "1234 Main Street Anytown Anystate 00000 USA",
                "gender": "Not Applicable",
                "nationality": "N/A",
                "registration_number": "000000",
                "name": "XYZ Widget Corporation",
                "shareholder_type": "Corporate",
                "phone_number": "0123456789",
            },
        ],
        "proprietors": [],
        "documents": {"search_certificate": ""},
        "directors": [
            {
                "shareholdings": "100000",
                "id_number": "A000000",
                "address": "678 Victoria Island, Lagos",
                "occupation": "CEO",
                "gender": "MALE",
                "nationality": "Nigerian",
                "date_of_birth": "2000-09-20",
                "name": "Joe Doe Leo",
                "id_type": "Passport",
                "phone_number": "0123456789",
            },
            {
                "shareholdings": "100000",
                "id_number": "A000000",
                "address": "1234 Main Street Anytown Anystate 00000 USA",
                "occupation": "COO",
                "gender": "FEMALE",
                "nationality": "American",
                "date_of_birth": "2000-01-01",
                "name": "Jane Doe",
                "id_type": "Passport",
                "phone_number": "0123456789",
            },
        ],
        "success": True,
    }

def test_error_return_data(
    client_kyb: BusinessVerification,
    kyb_partner_params: Dict[str, Any],
    kyb_id_info: Dict[str, str],
) -> None:
    """Validate Error retrun data"""
    kyb_partner_params["job_type"] = JobType.BUSINESS_VERIFICATION
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

            client_kyb.submit_job(kyb_partner_params, kyb_id_info)
    assert (
        str(value_error.value)
        == "Failed to post entity to https://testapi.smileidentity.com/v1/"
        "business_verification, status=400, response={'code': '2204', "
        "'error': 'unauthorized'}"
    )

def test_validate_return_data(
    kyb_partner_params: Dict[str, Any],
    kyb_id_info: Dict[str, str],
    client_kyb: BusinessVerification,
    signature_fixture: Signature,
) -> None:
    """Validate KYB responses output on successful job_submit"""
    signature_fixture.generate_signature()
    with patch("requests.post") as mocked_post:
        mocked_post.return_value.status_code = 200
        mocked_post.return_value.ok = True
        response = client_kyb.submit_job(kyb_partner_params, kyb_id_info)
        assert response is not None
        assert get_id_response(signature_fixture) is not None
