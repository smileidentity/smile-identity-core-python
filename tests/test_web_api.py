""" Test class for Web API"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from requests import Response

import pytest
import responses
from typing import cast

from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.types import ImageParams, OptionsParams, SignatureParams
from smile_id_core.Utilities import Utilities
from smile_id_core.WebApi import WebApi
from tests.conftest import (
    assert_request_called_with,
    stub_get_job_status,
    stub_upload_request,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")

"""Checks through unittests that all function in Web API application file
are tested"""


def test_handle_wrong_credentials(
    setup_web_client: Tuple[str, str, str, str]
) -> None:
    """Setups/initialises relevant params for tests and validates them"""
    api_key, partner_id, sid_server, callback_url = setup_web_client
    sid_server = "90"
    web_api = WebApi(partner_id, api_key, callback_url, sid_server)
    assert web_api.url == "90"
    web_api = WebApi(partner_id, callback_url, api_key, 0)
    pytest.raises(
        ValueError,
        WebApi,
        partner_id,
        callback_url,
        None,
        0,
    )
    pytest.raises(ValueError, WebApi, None, callback_url, api_key, 0)


def test_instance(
    setup_web_client: Tuple[str, str, str, str],
    client_utilities: Utilities,
) -> None:
    """Performs value checks on partner id, api key, callback url
    and endpoint url"""
    _, partner_id, _, callback_url = setup_web_client
    assert partner_id == "001"
    assert callback_url == "https://a_callback.com"
    assert client_utilities.url == "https://testapi.smileidentity.com/v1"


def test_no_image_params(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
) -> None:
    """Checks for when image_params is None"""
    partner_params, id_info_params = (
        web_partner_params,
        kyc_id_info,
    )
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            partner_params,
            None,  # type: ignore
            id_info_params,
            option_params,
        )
    assert (
        str(value_error.value)
        == "Please ensure that you send through image details"
    )


def test_no_callback_url_jt5(
    setup_web_client: Tuple[str, str, str, str],
    web_partner_params: Dict[str, Any],
    image_params: List[ImageParams],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
) -> None:
    """callback url is empty and job type is Enhanced KYC"""
    api_key, partner_id, sid_server, callback_url = setup_web_client
    web_api = WebApi(partner_id, callback_url, api_key, sid_server)
    web_partner_params["job_type"] = JobType.ENHANCED_KYC
    pytest.raises(
        ValueError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        kyc_id_info,
        option_params,
        True,
    )


def test_no_id_info_params_jt5(
    web_partner_params: Dict[str, Any],
    setup_web_client: Tuple[str, str, str, str],
    image_params: List[ImageParams],
    option_params: OptionsParams,
) -> None:
    """Checks when All id_info_params values are empty and job type is
    enhanced KYC"""
    web_partner_params["job_type"] = JobType.ENHANCED_KYC
    api_key, partner_id, sid_server, callback_url = setup_web_client
    web_api = WebApi(
        partner_id,
        callback_url,
        api_key,
        sid_server,
    )

    pytest.raises(
        ValueError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        {},
        option_params,
        True,
    )

    web_partner_params["job_type"] = JobType.BIOMETRIC_KYC
    web_api = WebApi(
        partner_id,
        callback_url,
        api_key,
        sid_server,
    )

    pytest.raises(
        ServerError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        {},
        option_params,
        True,
    )


def test_no_option_params(
    setup_web_client: Tuple[str, str, str, str],
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, Any],
    image_params: List[ImageParams],
) -> None:
    """Validates when no option params is provided(empty or None)"""
    api_key, partner_id, sid_server, callback_url = setup_web_client
    callback_url = ""
    web_api = WebApi(partner_id, callback_url, api_key, sid_server)
    pytest.raises(
        ValueError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        kyc_id_info,
        callback_url,
        True,
    )


def test_validate_return(
    option_params: OptionsParams,
    setup_web_client: Tuple[str, str, str, str],
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    image_params: List[ImageParams],
) -> None:
    """Validates on return data from WebAPi submit_job module call"""
    api_key, partner_id, sid_server, _ = setup_web_client
    web_api = WebApi(partner_id, "", api_key, sid_server)
    option_params["return_job_status"] = False
    pytest.raises(
        ValueError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        kyc_id_info,
        option_params,
        False,
    )


def test__validate_options(
    setup_web_client: Tuple[str, str, str, str],
    option_params: OptionsParams,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    image_params: List[ImageParams],
) -> None:
    """Performs checks for when option_params return_job_status is
    false"""
    api_key, partner_id, _, _ = setup_web_client
    web_api = WebApi(partner_id, "calback_url", api_key, 0)
    option_params["return_job_status"] = False
    pytest.raises(
        ValueError,
        web_api.submit_job,
        web_partner_params,
        image_params,
        kyc_id_info,
        option_params,
        True,
    )


def test_no_partner_params(
    client_web: WebApi,
    image_params: List[ImageParams],
    option_params: OptionsParams,
    kyc_id_info: Dict[str, str],
) -> None:
    """Checks/Handles no partner_params (None)"""

    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            None,  # type: ignore
            image_params,
            kyc_id_info,
            option_params,
        )
    assert (
        str(value_error.value)
        == "Please ensure that you send through partner params"
    )


@responses.activate
def test_success_true_smile_job_type(
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    image_params: List[ImageParams],
    option_params: OptionsParams,
    client_web: WebApi,
    signature_fixture: Signature,
) -> None:
    """check return data for valid smile_job_type when option_params
    return_job_status is false"""
    signature = get_signature(signature_fixture)
    stub_upload_request(signature)
    signature["timestamp"] = (datetime.now() - timedelta(days=1)).isoformat()
    stub_get_job_status(signature, True)
    stub_get_job_status(signature, True, "ERROR MSG")
    option_params["return_job_status"] = False

    # TODO: Modify this code; shouldn't be hardcoded
    assert client_web.submit_job(
        web_partner_params,
        image_params,
        kyc_id_info,
        option_params,
        False,
    )
    #  == {"success": True, "smile_job_id": "0000000857"},)


def test_missing_partner_params_for_at_least_1_param(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, Any],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
    """Checks/Handles no partner_params (None)"""

    web_partner_params["user_id"] = None
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert (
        str(value_error.value)
        == "Partner Parameter Arguments may not be null or empty"
    )

    web_partner_params["job_id"] = None
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert (
        str(value_error.value)
        == "Partner Parameter Arguments may not be null or empty"
    )

    web_partner_params["job_type"] = None
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert (
        str(value_error.value)
        == "Partner Parameter Arguments may not be null or empty"
    )


def test_id_info_params(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
    """This test raises an error when at least one of the id_info_params
    value is missing. Performs checks for country, id_type, and id_number
    """

    kyc_id_info["country"] = None  # type: ignore
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert str(value_error.value) == "key country cannot be empty"

    kyc_id_info["id_number"] = None  # type: ignore
    kyc_id_info["country"] = "NG"
    web_partner_params["job_type"] = JobType.BIOMETRIC_KYC
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert str(value_error.value) == "key id_number cannot be empty"


def test_non_valid_image(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
    """Checks for invalid images/non-existent images"""

    image_params.append(
        {
            "image_type_id": 0,
            "file_name": "path/to/image.jpg",
        }
    )
    with pytest.raises(FileNotFoundError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
        )
    assert (
        str(value_error.value) == "No such file or directory path/to/image.jpg"
    )


def test_boolean_options_params_non_jt5(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
    """Checks that option_params' return_job_status key is a boolean"""

    option_params["return_job_status"] = "Test"  # type: ignore
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            False,
        )
    assert str(value_error.value) == "return_job_status needs to be a boolean"
    option_params["return_job_status"] = True
    option_params["return_history"] = "tEST"  # type: ignore
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            True,
        )
    assert str(value_error.value) == "return_history needs to be a boolean"

    option_params["return_images"] = "tEST"  # type: ignore
    option_params["return_history"] = True
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            False,
        )
    assert str(value_error.value) == "return_images needs to be a boolean"

    option_params["return_images"] = True
    option_params["signature"] = "tEST"  # type: ignore
    with pytest.raises(ValueError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            False,
        )
    assert str(value_error.value) == "signature needs to be a boolean"


@responses.activate
def test_submit_job_should_raise_error_when_pre_upload_fails(
    client_web: WebApi,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
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

    with pytest.raises(ServerError) as value_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            False,
        )
    assert (
        str(value_error.value) == "Failed to post entity to"
        " https://testapi.smileidentity.com/v1/upload, status=400,"
        " response={'code': '2204', 'error': 'unauthorized'}"
    )


@responses.activate
def test_submit_job_should_raise_error_when_upload_fails(
    setup_web_client: Tuple[str, str, str, str],
    signature_fixture: Signature,
    client_web: WebApi,
    kyc_id_info: Dict[str, str],
    web_partner_params: Dict[str, Any],
    image_params: List[ImageParams],
    option_params: OptionsParams,
) -> None:
    """Validation to check if image upload fails"""
    signature = get_signature(signature_fixture)
    error = "Failed to upload zip"
    post_response = stub_upload_request(signature, error)
    api_key, partner_id, sid_server, _ = setup_web_client
    with pytest.raises(ServerError) as server_error:
        client_web.submit_job(
            web_partner_params,
            image_params,
            kyc_id_info,
            option_params,
            False,
        )

    response = {"code": "2205", "error": error}
    assert (
        str(server_error.value)
        == f"Failed to post entity to {post_response['upload_url']},"
        f" status=400, response={response}"
    )

    # Validate for jobtype not equal to 5 (JobType.ENHANCED_KYC)
    utilities = Utilities(partner_id, api_key, sid_server)
    assert utilities.validate_partner_params(web_partner_params) is None

    # web_api = WebApi("001", "https://a_callback.com", api_key, 0)


@responses.activate
def test_validate_return_data(
    client_web: WebApi,
    signature_fixture: Signature,
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    image_params: List[ImageParams],
) -> None:
    """Checks return data validity from web API job submission"""

    signature = get_signature(signature_fixture)
    stub_upload_request(signature)
    stub_get_job_status(signature, False)
    job_status_response = stub_get_job_status(signature, True)

    response = client_web.submit_job(
        web_partner_params,
        image_params,
        kyc_id_info,
        option_params,
        False,
    )

    assert response
    assert cast(Response, response).json() == job_status_response["json"]


@responses.activate
def test_get_web_token(
    client_web: WebApi, signature_fixture: Signature
) -> None:
    """Creates an authorization token used in Hosted Web Integration"""
    responses.add(
        responses.POST,
        "https://testapi.smileidentity.com/v1/token",
        status=400,
        json={"error": "Invalid product.", "code": "2217"},
    )
    signature = get_signature(signature_fixture)
    user_id = "user_id"
    job_id = "job_id"
    product = "product_type"
    client_web.get_web_token(
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
    assert_request_called_with(
        "https://testapi.smileidentity.com/v1/token", responses.POST, body
    )


def get_signature(signature_fixture: Signature) -> SignatureParams:
    return signature_fixture.generate_signature(
        timestamp=datetime.now().isoformat()
    )


def test_poll_job_status(
    web_partner_params: Dict[str, Any],
    kyc_id_info: Dict[str, str],
    option_params: OptionsParams,
    signature_fixture: Signature,
    client_web: WebApi,
) -> None:
    pytest.raises(
        ServerError,
        client_web.poll_job_status,
        5,
        web_partner_params,
        kyc_id_info,
        None,
    )
    assert client_web.signature_params is not None

    pytest.raises(
        ServerError,
        client_web.poll_job_status,
        5,
        web_partner_params,
        option_params,
        signature_fixture.generate_signature(None),
    )
    client_web.utilities = None
    pytest.raises(
        ValueError,
        client_web.poll_job_status,
        5,
        web_partner_params,
        option_params,
        signature_fixture.generate_signature(None),
    )
