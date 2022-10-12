"""Defines signature class for Smile Identity Core API."""
import base64
import hashlib
import hmac
import typing
from datetime import datetime

__all__ = ["Signature"]

SignatureType = typing.Dict[str, str]


class Signature:
    """Class for generating signature for Smile Identity Core API."""

    def __init__(self, partner_id: str, api_key: str):
        """Initialize signature class.

        Args:
            partner_id (str): Smile Identity partner id.
                Usually a 3 or 4 digit number. May contain leading zeros.
            api_key (str): Smile Identity API key.
                Please visit https://portal.smileidentity.com/api-key to get your API key.

        Raises:
            ValueError: If partner_id or api_key is not a string.
        """
        if not isinstance(partner_id, str):
            raise ValueError("partner_id must a string.")
        if not isinstance(api_key, str):
            raise ValueError("api_key must be a string.")

        self.partner_id: str = partner_id
        self.api_key: str = api_key

    def generate_signature(
        self, timestamp: typing.Optional[str] = None
    ) -> SignatureType:
        """Generate signature for Smile Identity Core API.

        Args:
            timestamp (str, optional): Timestamp in ISO 8601 format. Defaults to None.

        Returns:
            SignatureType: Dictionary with signature and timestamp keys with string values.
        """
        if not isinstance(timestamp, str):
            timestamp = datetime.now().isoformat()
        hmac_new: hmac.HMAC = hmac.new(
            self.api_key.encode("utf-8"),
            digestmod=hashlib.sha256,
        )
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(self.partner_id).encode("utf-8"))
        hmac_new.update(b"sid_request")
        calculated_signature: bytes = base64.b64encode(hmac_new.digest())
        return {
            "signature": calculated_signature.decode("utf-8"),
            "timestamp": timestamp,
        }

    def confirm_signature(self, timestamp: str, msg_signature: str) -> bool:
        """Confirm signature for Smile Identity Core API.

        Args:
            timestamp (str): Timestamp in ISO 8601 format.
            msg_signature (str): Signature

        Returns:
            bool: True if signature is valid, False otherwise.
        """
        return self.generate_signature(timestamp)["signature"] == msg_signature
