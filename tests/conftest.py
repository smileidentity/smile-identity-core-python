"""Fixture file to allow for code re-usability and reduce duplication."""
import base64
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4

import pytest
import responses
from Crypto.PublicKey import RSA

from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.constants import JobType
from smile_id_core.IdApi import IdApi
from smile_id_core.Signature import Signature
from smile_id_core.types import ImageParams, OptionsParams, SignatureParams
from smile_id_core.Utilities import Utilities
from smile_id_core.WebApi import WebApi

@pytest.fixture(scope="function")
def setup_client() -> Tuple[str, str, str]:
    """Setups/initialises relevant params for tests and validates them."""
    key = RSA.generate(2048)
    public_key = key.publickey().export_key()
    api_key: str = base64.b64encode(public_key).decode("UTF-8")
    partner_id: str = "001"
    sid_server = "0"
    return api_key, partner_id, sid_server

@pytest.fixture(scope="function")
def setup_web_client() -> Tuple[str, str, str, str]:
    """Setups/initialises relevant params for tests and validates them."""
    key = RSA.generate(2048)
    public_key = key.publickey().export_key()
    api_key: str = base64.b64encode(public_key).decode("UTF-8")
    partner_id: str = "001"
    sid_server = "0"
    callback_url = str(
        "https://a_callback.com",
    )
    return api_key, partner_id, sid_server, callback_url

@pytest.fixture(scope="function")
def kyc_partner_params() -> Dict[str, Any]:
    """Reset partner_params parameters for kyc jobs."""
    partner_params: Dict[str, Any] = {
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "job_type": JobType.ENHANCED_KYC,
    }

    return partner_params

@pytest.fixture(scope="function")
def kyc_id_info() -> Dict[str, str]:
    """Reset id_info_params parameters for kyc jobs."""
    id_info_params: Dict[str, str] = {
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

    return id_info_params

@pytest.fixture(scope="function")
def kyb_partner_params() -> Dict[str, Any]:
    """Fixture initializes(resets) partner_params for kyb jobs."""
    partner_params: Dict[str, Any] = {
        "user_id": "kyb_test_user_008",
        "job_id": "job_id_001",
        "job_type": JobType.BUSINESS_VERIFICATION,
    }
    return partner_params

@pytest.fixture(scope="function")
def web_partner_params() -> Dict[str, Any]:
    """Define partner_params with biometric_kyc as jobtype for webapi calls."""
    partner_params = {
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "job_type": JobType.BIOMETRIC_KYC,
    }
    return partner_params

@pytest.fixture(scope="function")
def option_params() -> OptionsParams:
    """Initialize option_params; sets them all to True."""
    options_params: OptionsParams = {
        "return_job_status": True,
        "return_history": True,
        "return_images": True,
        "use_enrolled_image": True,
    }
    return options_params

@pytest.fixture(scope="function")
def image_params() -> List[ImageParams]:
    """Generate base64 image, define image type and return as image_param."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")
    image_param: List[ImageParams] = []
    with open(image_path, "rb") as binary_file:
        base64_data = base64.b64encode(binary_file.read())
        base64_str = base64_data.decode("utf-8")

    image_param.append(
        {
            "image_type_id": 2,
            "image": base64_str,
        }
    )
    return image_param

@pytest.fixture(scope="function")
def kyb_id_info() -> Dict[str, str]:
    """Fixture initializes(resets) id_info_params for kyb jobs."""
    id_info_params: Dict[str, str] = {
        "country": "NG",
        "id_type": "BUSINESS_REGISTRATION",
        "id_number": "0000000",
        "business_type": "co",
        "partner_id": "001",
    }
    return id_info_params

@pytest.fixture(scope="function")
def client(setup_client: Tuple[str, str, str]) -> IdApi:
    """Create IdApi object for kyc job."""
    api_key, partner_id, sid_server = setup_client
    id_api = IdApi(partner_id, api_key, sid_server)
    return id_api

@pytest.fixture(scope="function")
def client_kyb(setup_client: Tuple[str, str, str]) -> BusinessVerification:
    """Create BusinessVerification object for kyb job."""
    api_key, partner_id, sid_server = setup_client
    kyb_api = BusinessVerification(partner_id, api_key, sid_server)
    return kyb_api

@pytest.fixture(scope="function")
def client_web(setup_client: Tuple[str, str, str]) -> WebApi:
    """Create BusinessVerification object for kyb job."""
    api_key, partner_id, sid_server = setup_client
    web_api = WebApi(partner_id, "https://a_callback.com", api_key, sid_server)
    return web_api

@pytest.fixture(scope="function")
def client_utilities(setup_client: Tuple[str, str, str]) -> Utilities:
    """Create BusinessVerification object for kyb job."""
    api_key, partner_id, sid_server = setup_client
    utilities = Utilities(partner_id, api_key, sid_server)
    return utilities

@pytest.fixture(scope="function")
def signature_fixture(setup_client: Tuple[str, str, str]) -> Signature:
    """Create signature object for jobs that use the signature class."""
    api_key, partner_id, _ = setup_client
    return Signature(partner_id, api_key)

@pytest.fixture(scope="function")
def signature_params(signature_fixture: Signature) -> SignatureParams:
    """Uses signature_fixture to create a SignatureParam."""
    signature = signature_fixture.generate_signature(datetime.now().isoformat())
    return signature

@pytest.fixture(scope="function")
def partner_params_jt6() -> Dict[str, Any]:
    """Define partner params for jobtype 6 (Document verification)."""
    partner_params = {
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "job_type": JobType.DOCUMENT_VERIFICATION,
    }
    return partner_params

@pytest.fixture(scope="function")
def partner_params_util() -> Dict[str, Any]:
    """Define partner params for utitlity test class."""
    partner_params = {
        "user_id": str(uuid4()),
        "job_id": str(uuid4()),
        "job_type": JobType.BIOMETRIC_KYC,
    }

    return partner_params

def get_job_status_response(
    signature_params: SignatureParams,
    job_complete: bool = True,
) -> Dict[str, Any]:
    """Return a job status response."""
    return {
        "signature": signature_params.get("signature"),
        "timestamp": signature_params.get("timestamp"),
        "job_complete": job_complete,
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
                "job_type": 4,
            },
            "ConfidenceValue": "100",
            "IsMachineResult": "true",
        },
        "image_links": {
            "selfie_image": "https://smile-fr-results.s3.us-west-2."
            "amazonaws.com/test/000000/023/023-0000001897-"
            "LoRSpxJUzmYgYS2R00XpaHJYLOiNXN/SID_Preview_FULL.jpg"
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                },
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                },
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                    "ExpirationDate": "Not Available",
                },
            },
        ],
    }

def stub_get_job_status(
    signature_key: SignatureParams,
    job_complete: bool = True,
    with_error: Any = None,
) -> Dict[str, Any]:
    """Stub to get job status from POST request.

    argument(s):
    signature_key: Dict[str, str],
    job_complete: Boolean value that specifies if job completed or not
    with_error: Specifies error mesaage
    """
    if with_error:
        job_status_response = {
            "status": 400,
            "json": {"code": "2098", "error": with_error},
        }
    else:
        job_status_response = {
            "status": 200,
            "json": get_job_status_response(signature_key, job_complete),
        }

    responses.add(
        responses.POST,
        "https://testapi.smileidentity.com/v1/job_status",
        **job_status_response,  # type: ignore
    )
    return job_status_response

def get_pre_upload_response(signature_key: SignatureParams) -> Dict[str, Any]:
    """Return pre-upload response as stub for testing."""
    return {
        "signature": signature_key.get("signature"),
        "timestamp": signature_key.get("timestamp"),
        "upload_url": "https://some_url.com",
        "smile_job_id": "0000000857",
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
                "job_type": 4,
            },
            "ConfidenceValue": "100",
            "IsMachineResult": "true",
        },
        "image_links": {
            "selfie_image": "https://smile-fr-results.s3.us-west-2."
            "amazonaws.com/test/000000/023/023-0000001897-"
            "LoRSpxJUzmYgYS2R00XpaHJYLOiNXN/SID_Preview_FULL.jpg"
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                },
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                },
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
                    "optional_info": (
                        "Partner can put whatever they want as long as it"
                        " is a string"
                    ),
                    "more_optional_info": (
                        "There can be as much or as little or no optional"
                        " info"
                    ),
                    "ExpirationDate": "Not Available",
                },
            },
        ],
    }

def stub_upload_request(
    signature: SignatureParams, fail_with_message: str = None  # type: ignore
) -> Dict[str, Any]:
    """Stub to get upload request.

    argument(s):
        signature: Dict containing uniquely generated signature and a
        timestamp
        fail_with_message: str or None (Any) Error message for failure.

    Returns:
        Returns post response from _get_pre_upload_response function.
        This is a dictionary of string to string
    """
    post_response = get_pre_upload_response(signature)
    responses.add(
        responses.POST,
        "https://testapi.smileidentity.com/v1/upload",
        status=200,
        json=post_response,
    )
    upload_response = {"status": 200, "json": {}}
    if fail_with_message:
        upload_response = {
            "status": 400,
            "json": {"code": "2205", "error": fail_with_message},
        }
    responses.add(
        responses.PUT,
        post_response["upload_url"],
        **upload_response,  # type: ignore
    )
    return post_response

def assert_request_called_with(
    url: str, method: Any, body: Dict[str, Any]
) -> None:
    """Validate request response outputs with these parameters.

    url: url to endpoint
    method: Post request method call
    body: A dictionary containing the data payload
    """
    called_requests = [
        call.request
        for call in responses.calls
        if call.request.url == url and call.request.method == method
    ]
    size = len(called_requests)
    if size == 0:
        pytest.fail(f"{method} {url} not called")
    else:
        found = False
        for request in called_requests:
            try:
                assert request.body == json.dumps(body)
                found = True
            except AssertionError:
                pass
        if not found:
            pytest.fail(f"No request match call with body {body}")
