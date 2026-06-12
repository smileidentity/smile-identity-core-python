"""Test class for the SIgnature class"""

import os
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Tuple

import pytest

from smile_id_core.Signature import Signature


def test_no_partner_id_api_key(
    setup_client: Tuple[str, str, str], signature_fixture: Signature
) -> None:
    """Validates API key from signature object"""
    api_key, partner_id, _ = setup_client
    assert api_key == signature_fixture.api_key
    pytest.raises(ValueError, Signature, partner_id, None)
    pytest.raises(ValueError, Signature, None, api_key)


def test_generate_signature(
    setup_client: Tuple[str, str, str],
    signature_fixture: Signature,
) -> None:
    """Generates and validates generated singature"""
    timestamp = datetime.now(timezone.utc).isoformat()
    api_key, partner_id, _ = setup_client
    signature = signature_fixture.generate_signature(timestamp=timestamp)
    assert signature["timestamp"] == timestamp

    hmac_new = hmac.new(api_key.encode(), digestmod=hashlib.sha256)
    hmac_new.update(timestamp.encode("utf-8"))
    hmac_new.update(str(partner_id).encode("utf-8"))
    hmac_new.update("sid_request".encode("utf-8"))
    calculated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

    assert signature["signature"] == calculated_signature


def test_confirm_signature(
    setup_client: Tuple[str, str, str],
    signature_fixture: Signature,
) -> None:
    """Validates confirm_signature accepts valid and rejects invalid signatures"""
    api_key, partner_id, _ = setup_client
    timestamp = datetime.now(timezone.utc).isoformat()

    # should confirm a valid incoming signature
    hmac_new = hmac.new(api_key.encode("utf-8"), digestmod=hashlib.sha256)
    hmac_new.update(timestamp.encode("utf-8"))
    hmac_new.update(str(partner_id).encode("utf-8"))
    hmac_new.update("sid_request".encode("utf-8"))
    valid_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

    assert (
        signature_fixture.confirm_signature(timestamp, valid_signature) is True
    )

    # should reject a signature that does not match
    fake_signature = base64.b64encode(os.urandom(32)).decode("utf-8")
    assert (
        signature_fixture.confirm_signature(timestamp, fake_signature) is False
    )
