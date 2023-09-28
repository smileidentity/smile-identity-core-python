"""Utilities Class allows to query information on submitted job status.

Additionally, the Utilities class makes a call to the Signature class and
performs signature parama validation.
"""
import json
import re
import sys
from typing import Any, Dict, Optional, Union

import requests
from requests import Response

from smile_id_core import constants
from smile_id_core.base import Base
from smile_id_core.constants import JobType
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.types import OptionsParams, SignatureParams

# import importlib.metadata if available, otherwise importlib_metadata
# (for Python < 3.8)
if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

__all__ = [
    "Utilities",
    "get_signature",
    "get_version",
    "validate_signature_params",
]

sid_server_map = constants.sid_server_map


def get_version() -> str:
    """Return the module version number specified in pyproject.toml.

    Returns:
        str: The module version number
    """
    return importlib_metadata.version(__package__)


class Utilities(Base):
    """Query information on subitted job status."""

    def __init__(
        self, partner_id: str, api_key: str, sid_server: Union[int, str]
    ):
        """Initialize all relevant params required for Utilities methods.

        argument(s):
            partner_id: distinct identification number for a partner
            api_key(str): api_key obtained from the partner portal
            sid_server(str or int): specifies production or sandbox
        """
        super().__init__(partner_id, api_key, sid_server)

    def get_job_status(
        self,
        partner_params: Dict[str, Any],
        option_params: OptionsParams,
        signature: Optional[SignatureParams] = None,
    ) -> Dict[str, Any]:
        """Validate params (signature & partner) and queries job status.

        argument(s):
        partner_params: Dict containing all partner params (job_id, user_id,
            job_type)
        option_params: Dict containaing optional info params such as
            return_job_status, return_image_links, and return_history.
            Each of these keys has a boolean value

        Returns:
        Makes a call to _query_job_status which returns job_status of type
        Dict[str, Any].
        """
        if signature is None:
            signature = get_signature(self.partner_id, self.api_key)

        validate_signature_params(signature)
        # validate_partner_param throws an error if job_type is empty/not
        # provided, but it's not required by get_job_status
        Utilities.validate_partner_params(
            {
                **partner_params,
                "job_type": partner_params.get("job_type", "1"),
            }
        )
        if not option_params or option_params is None:
            options = OptionsParams(
                return_job_status=True,
                return_history=False,
                return_images=False,
                use_enrolled_image=False,
            )
        else:
            options = option_params
        return self.query_job_status(
            str(partner_params.get("user_id")),
            str(partner_params.get("job_id")),
            options,
            signature,
        )

    def query_job_status(
        self,
        user_id: str,
        job_id: str,
        option_params: OptionsParams,
        signature: SignatureParams,
    ) -> Dict[str, Any]:
        """Make post request, checks validity of job status response/code.

        argument(s):
        user_id: A unique string representing user's ID
        job_id: Unique job id
        option_params: Dict containaing optional info params such as
            return_job_status, return_image_links, and return_history.
            Each of these keys has a boolean value
        signature: Dictionary of a uniquely generated signature value and
            a timestamp

        Returns:
            Returns status if status code passes. This is of type Dict[str, Any]
        """
        job_status = Utilities.execute_post(
            f"{self.url}/job_status",
            self.configure_job_query(
                user_id,
                job_id,
                option_params,
                signature,
            ),
        )

        if job_status.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/job_status,"
                f" response={job_status.status_code}:{job_status.reason} -"
                f" {job_status.json()}"
            )
        job_status_json_resp = job_status.json()
        timestamp = job_status_json_resp["timestamp"]
        server_signature = job_status_json_resp["signature"]
        new_signature = Signature(self.partner_id, self.api_key)
        valid = new_signature.confirm_signature(timestamp, server_signature)
        if not valid:
            raise ServerError(
                "Unable to confirm validity of the job_status response"
            )
        return dict(job_status.json())

    def configure_job_query(
        self,
        user_id: str,
        job_id: str,
        options: OptionsParams,
        signature: SignatureParams,
    ) -> Dict[str, Any]:
        """Return partner_id, job_id, user_id, and some option_params values.

        argument(s):
        user_id(str): unique user id
        job_id: unique job id
        option_params: Dictionary containaing optional info params such as
            return_job_status, return_image_links, and return_history.
            Each of these keys has a boolean value
        signature: Dictionary of a uniquely generated signature value and
            a timestamp

        Return:
        Returns some partner info, option params and signature data as a
        dictionary.
        """
        return {
            **signature,
            "partner_id": self.partner_id,
            "job_id": job_id,
            "user_id": user_id,
            "image_links": options.get("return_images"),
            "history": options.get("return_history"),
        }

    @staticmethod
    def validate_partner_params(partner_params: Dict[str, Any]) -> None:
        """Validate partner_params content.

        argument(s):
        Partner_params: Dictionary containing partner params info
        """
        if not partner_params:
            raise ValueError(
                "Please ensure that you send through partner params"
            )

        if (
            not partner_params.get("user_id")
            or not partner_params.get("job_id")
            or not partner_params.get("job_type")
        ):
            raise ValueError(
                "Partner Parameter Arguments may not be null or empty"
            )

        if not isinstance(partner_params.get("user_id"), str):
            raise ValueError("Please ensure user_id is a string")

        if not isinstance(partner_params.get("job_id"), str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params.get("job_type"), int):
            raise ValueError("Please ensure job_type is a number")

    @staticmethod
    def validate_id_params(
        sid_server: Union[str, int],
        id_info_params: Dict[str, Any],
        partner_params: Dict[str, Any],
    ) -> None:
        """Validate id info parameters.

        argument(s):
        sid_server:
        id_info_params:
        partner_params:
        """
        job_type = partner_params.get("job_type")
        is_docv_job = (
            job_type == JobType.DOCUMENT_VERIFICATION
            or job_type == JobType.ENHANCED_DOCUMENT_VERIFICATION
        )
        if not is_docv_job and not id_info_params.get("entered"):
            return

        country = id_info_params.get("country")
        if (
            not country
            or not isinstance(country, str)
            or not re.match(r"^[A-Z]{2}$", country)
        ):
            raise ValueError(
                "key country must be a valid 2-letter ISO 3166-1 alpha-2 country code."
            )

        if job_type == JobType.DOCUMENT_VERIFICATION:
            return
        elif job_type == JobType.ENHANCED_DOCUMENT_VERIFICATION:
            if not id_info_params.get("id_type"):
                raise ValueError("key id_type cannot be empty")
        elif not id_info_params.get("id_number"):
            raise ValueError("key id_number cannot be empty")

    @staticmethod
    def execute_get(url: str) -> Response:
        """Send Get request to url endpoint.

        argument(s):
        url: Url endpoint string
        """
        resp = requests.get(
            url=url,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
        )
        return resp

    @staticmethod
    def execute_post(url: str, payload: Dict[str, str]) -> Response:
        """Make post request to specified url with payload data.

        argument(s):
        url: str: endpoint url
        payload: data payload to be sent to url

        Returns: Response from post request to endpoint
        """
        data = json.dumps(payload)
        resp = requests.post(
            url=url,
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )
        return resp

    @staticmethod
    def execute_http(url: str, payload: Dict[str, Response]) -> Response:
        """Send http request to specified endpoint url and return response.

        argument(s):
        url: Endpoint url based on api key
        payload: Dictionary containing payload data
        Returns:
        Returns Response form post request
        """
        data = json.dumps(payload)

        resp = requests.post(
            url=url,
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )
        return resp

    def configure_json(
        self,
        partner_params: Dict[str, Any],
        id_params: Dict[str, str],
        signature: SignatureParams,
    ) -> Dict[str, Any]:
        """Configure JSON request payload by merging job params.

        argument(s):
        partner_params (Dict[str, Any]): Dictionary of partner parameters
        id_params (Dict[str, str]): Dictionary of ID parameters
        signature (Dict[str, str]): Dictionary of signature

        Returns:
        Merged dictionary of signature, partner_id, partner_params,
        source_sdk, and source_sdk_version of type Dict[str, Any]
        """
        validate_signature_params(signature)
        return {
            **signature,
            "partner_id": self.partner_id,
            "partner_params": partner_params,
            "source_sdk": "Python",
            "source_sdk_version": get_version(),
            **id_params,
        }


def validate_signature_params(signature_dict: SignatureParams) -> None:
    """Perform checks on existence of signature and timestamp keys.

    argument(s):
    signature_dict: SIgnature params dictionary (timestamp and signature)
    """
    if not signature_dict.get("signature"):
        raise Exception("Missing key, must provide a 'signature' field")
    if not signature_dict.get("timestamp"):
        raise Exception("Missing 'timestamp' field")


def get_signature(partner_id: str, api_key: str) -> SignatureParams:
    """Generate signature and returns its timestamp and signature.

    argument(s):
    partner_id: distinct identification number for a partner
    api_key: api key obtained from portal

    Returns: Dictionary containing timestamp and signature
    """
    signature_object = Signature(partner_id, api_key).generate_signature()
    return SignatureParams(
        timestamp=signature_object["timestamp"],
        signature=signature_object["signature"],
    )
