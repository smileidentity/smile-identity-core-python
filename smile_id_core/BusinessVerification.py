"""ID API class for Business Verification services.

This business verification class lets you search the business registration or
tax information of a business from one of our supported countries. The
business registration search will return the company information,
directors, beneficial owners and fiduciaries of a business while
the tax information returns only the company information
"""
from typing import Any, Dict, Union

from smile_id_core.base import Base
from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.Utilities import Utilities, get_signature

__all__ = ["BusinessVerification"]


class BusinessVerification(Base):
    """This is an API class that lets you perform KYB Services.

    It exports the ServerError, JobType, Utilities, and some existing
    methods in Utilities class (get_signature, get_version,
    validate_signature_params amd sid_server_map)
    """

    def __init__(
        self, partner_id: str, api_key: str, sid_server: Union[str, int]
    ):
        """Initialize all relevant params required for business verification.

        argument(s):
            partner_id: distinct identification number for a partner
            api_key(str): api_key obtained from the partner portal
            sid_server(str or int): specifies production or sandbox
        """
        super().__init__(partner_id, api_key, sid_server)
        self.utilities = Utilities(partner_id, api_key, sid_server)

    def submit_job(
        self,
        partner_params: Dict[str, Any],
        id_params: Dict[str, str],
    ) -> Dict[str, Any]:
        """Generate signature, creates payload and get response for KYb jobs.

        argument(s):
        partner_params: Dict containing all partner params (job_id, user_id,
            job_type)
        id_params: Dict containaing id info params such as country,
            business_type, id_number and id_type

        Returns:
            Dict[str, Any] which contains response to the HTTP post request.
        """
        Utilities.validate_partner_params(partner_params)

        if not id_params:
            raise ValueError(
                "Please ensure that you send through ID Information"
            )

        if partner_params.get("job_type") != JobType.BUSINESS_VERIFICATION:
            raise ValueError("Job type must be 7 for kyb")

        signature_object = get_signature(self.partner_id, self.api_key)
        self.utilities = Utilities(
            self.partner_id, self.api_key, self.sid_server
        )
        payload = self.utilities.configure_json(
            partner_params=partner_params,
            id_params=id_params,
            signature=signature_object,
        )
        url = f"{self.url}/business_verification"
        response = self.utilities.execute_http(url, payload)

        if response.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/business_verification,"
                f" status={response.status_code}, response={response.json()}"
            )
        return dict(response.json())
