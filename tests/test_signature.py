"""tests for Signature class"""
import base64
import hashlib
import hmac
import typing
from datetime import datetime

import pytest

from Crypto.PublicKey import RSA

from smile_id_core import Signature


def mock_api_key() -> str:
    """Generate a mock api key"""
    key = RSA.generate(2048)
    public_key = key.publickey().export_key()
    api_key = base64.b64encode(public_key).decode("UTF-8")
    return api_key


def test_generate_signature_invalid_api_key():
    """Test generate signature with invalid api key"""
    api_key = None
    partner_id: str = "001"

    with pytest.raises(ValueError) as value_error:
        Signature(partner_id, api_key)

    assert str(value_error.value) == "api_key must be a string."


def test_generate_signature_invalid_partner_id():
    """Test generate signature with invalid partner id"""

    api_key: str = mock_api_key()
    partner_id = None

    with pytest.raises(ValueError) as value_error:
        Signature(partner_id, api_key)

    assert str(value_error.value) == "partner_id must a string."


def test_generate_signature():
    """Test generate signature"""
    api_key: str = mock_api_key()
    partner_id: str = "001"
    signer: Signature = Signature(partner_id, api_key)
    timestamp: str = datetime.now().isoformat()
    signature: typing.Dict[str, str] = signer.generate_signature(timestamp=timestamp)

    assert "timestamp" in signature and isinstance(signature["timestamp"], str)
    assert "signature" in signature and isinstance(signature["signature"], str)

    assert signature["timestamp"] == timestamp

    hmac_new = hmac.new(api_key.encode(), digestmod=hashlib.sha256)
    hmac_new.update(timestamp.encode("utf-8"))
    hmac_new.update(str(partner_id).encode("utf-8"))
    hmac_new.update(b"sid_request")
    calculated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

    assert signature["signature"] == calculated_signature


def test_generate_signature_no_timestamp():
    """Test generate signature"""
    api_key: str = mock_api_key()
    partner_id: str = "001"
    signer: Signature = Signature(partner_id, api_key)
    signature: typing.Dict[str, str] = signer.generate_signature()

    assert "timestamp" in signature and isinstance(signature["timestamp"], str)
    assert "signature" in signature and isinstance(signature["signature"], str)

    assert signature["timestamp"] <= datetime.now().isoformat()

    hmac_new = hmac.new(api_key.encode(), digestmod=hashlib.sha256)
    hmac_new.update(signature["timestamp"].encode("utf-8"))
    hmac_new.update(str(partner_id).encode("utf-8"))
    hmac_new.update(b"sid_request")
    calculated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

    assert signature["signature"] == calculated_signature


def test_confirm_signature():
    """Test confirm signature"""
    api_key: str = mock_api_key()
    partner_id: str = "001"
    signer: Signature = Signature(partner_id, api_key)
    timestamp: str = datetime.now().isoformat()
    signature: typing.Dict[str, str] = signer.generate_signature(timestamp=timestamp)

    assert signer.confirm_signature(timestamp, signature["signature"])
