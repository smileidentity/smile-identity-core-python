"""This Signature class creates and validates generated signatures."""
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional

from smile_id_core.types import SignatureParams

__all__ = ["Signature"]


class Signature:
    """Generates signature for a given partner ID and API key.

    A generated signature is a dictionary containing a signature key and a
    timestamp key. Signatures are uniquely generated using hmac_new
    (a Python standard library's hmac module).
    """

    def __init__(self, partner_id: str, api_key: str) -> None:
        """Initialize all relevant params required for Signature generation.

        It also validation/checks for partner_id, api_key and signature params.

        argument(s):
        partner_id: distinct identification number for a partner
        sid_server: specifies production or sandbox (str or int)
        """
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key

    def generate_signature(
        self, timestamp: Optional[str] = None
    ) -> SignatureParams:
        """Generate a unique signature.

        argument(s):
        timestamp: string timestamp

        Returns:
        A dictionary containing generated signature and timestamp
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        hmac_new = hmac.new(
            self.api_key.encode("utf-8"), digestmod=hashlib.sha256
        )
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(self.partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))
        calculated_signature = base64.b64encode(hmac_new.digest())
        return SignatureParams(
            signature=calculated_signature.decode("utf-8"),
            timestamp=timestamp,
        )

    def confirm_signature(self, timestamp: str, msg_signature: str) -> bool:
        """Perform validation for a signature value.

        argument(s):
            timestamp: a timestamp string
            msg_signature: a signature string

        Returns:
            A bool based on signature message generated validation
        """
        return self.generate_signature(timestamp)["signature"] == msg_signature
