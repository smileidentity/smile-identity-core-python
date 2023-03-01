"""Fixture file to allow for code re-usability and reduce duplication."""
import base64
from typing import Any, Dict, Tuple
from uuid import uuid4

import pytest
from Crypto.PublicKey import RSA

from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.constants import JobType
from smile_id_core.IdApi import IdApi
from smile_id_core.Signature import Signature


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
def signature_fixture(setup_client: Tuple[str, str, str]) -> Signature:
    """Create signature object for jobs that use the signature class."""
    api_key, partner_id, _ = setup_client
    return Signature(partner_id, api_key)
