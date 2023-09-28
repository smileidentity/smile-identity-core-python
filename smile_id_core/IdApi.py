"""ID API class for kyc services."""
from typing import Any, Dict, Optional, Union

from smile_id_core.base import Base
from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.types import OptionsParams
from smile_id_core.Utilities import Utilities, get_signature

__all__ = ["IdApi"]


class IdApi(Base):
    """This API class that lets you perform KYC Services.

    These services include verifying an ID number as well as retrieve a user's
    Personal Information.
    """

    def __init__(
        self, partner_id: str, api_key: str, sid_server: Union[str, int]
    ):
        """Initialize all relevant params required for business verification.

        argument(s):
        partner_id: Distinct Smile partner id from the portal
        api_key: API key to access the portal
        sid_server: The server to use for the SID API. 0 for staging
        and 1 for production.
        """
        super().__init__(partner_id, api_key, sid_server)
        self.utilities = Utilities(partner_id, api_key, sid_server)

    def submit_job(
        self,
        partner_params: Dict[str, Any],
        id_params: Dict[str, str],
        options_params: Optional[OptionsParams] = None,
    ) -> Dict[str, Any]:
        """Validate data params & query id_verification endpoint for KYC jobs.

        Performs checks on id_info_params, partner_params, makes endpoint
        calls for KYC jobs and returns responses.

        argument(s):
        partner_params: Dictionary containing all partner params
        id_params: Dictionary containing id info params
        option_params: Dictionary containing optional info params such as
            return_job_status, return_image_links, and return_history.
            Each of these keys has a boolean value

        Returns: https post request output of type Response. Alternatively,
        raises a server or value error if there's an exception.
        """
        if not options_params:
            options_params = OptionsParams(
                return_job_status=False,
                return_history=False,
                return_images=False,
                use_enrolled_image=False,
            )

        Utilities.validate_partner_params(partner_params)
        if not id_params:
            raise ValueError(
                "Please ensure that you send through ID Information"
            )

        if partner_params.get("job_type") == JobType.BUSINESS_VERIFICATION:
            return BusinessVerification(
                self.partner_id, self.api_key, self.url
            ).submit_job(partner_params, id_params)

        Utilities.validate_id_params(
            self.url,
            id_params,
            partner_params,
        )

        if partner_params.get("job_type") != JobType.ENHANCED_KYC:
            raise ValueError("Job type must be 5 for ID Api")

        signature_object = get_signature(self.partner_id, self.api_key)
        payload = self.utilities.configure_json(
            partner_params, id_params, signature_object
        )
        url = f"{self.url}/id_verification"
        response = self.utilities.execute_http(url, payload)
        if response.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {url},"
                f" status={response.status_code}, response={response.json()}"
            )
        return dict(response.json())
