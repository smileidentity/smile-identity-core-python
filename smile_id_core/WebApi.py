"""WebAPI allows ID authority/third parties User validation by partners."""
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

import requests
from requests import Response

from smile_id_core.base import Base
from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.constants import JobType
from smile_id_core.IdApi import IdApi
from smile_id_core.image_upload import generate_zip_file, validate_images
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.types import ImageParams, OptionsParams, SignatureParams
from smile_id_core.Utilities import (
    Utilities,
    get_signature,
    get_version,
    validate_signature_params,
)

__all__ = ["WebApi"]


class WebApi(Base):
    """Allows validation of user ID against ID authority/third parties.

    Checks against relevant Identity Authorities/Third Party databases
    that Smile Identity has access to using ID information provided by the
    customer/user (including photo for compare).

    Attributes:
    partner_id (str): Smile partner id from the portal
    call_back_url(str): Callback url to endpoint
    """

    def __init__(
        self,
        partner_id: str,
        call_back_url: str,
        api_key: str,
        sid_server: Union[str, int],
    ):
        """Set ups environment and initialises params.

        argument(s):
        partner_id: distinct id of partner
        call_back_url(str): Callback url to endpoint
        api_key: api key from the partner portal
        sid_server: The server to use for the SID API. 0 for staging and 1 for
            production.
        """
        super().__init__(partner_id, api_key, sid_server)
        self.call_back_url = call_back_url
        self.utilities: Optional[Utilities] = Utilities(
            self.partner_id, self.api_key, self.sid_server
        )
        self.signature_params = get_signature(self.partner_id, self.api_key)

    def __call_id_api(
        self,
        partner_params: Dict[str, Any],
        id_info_params: Dict[str, str],
        options_params: OptionsParams,
    ) -> Dict[str, Any]:
        id_api = IdApi(self.partner_id, self.api_key, self.sid_server)
        return id_api.submit_job(partner_params, id_info_params, options_params)

    def submit_job(
        self,
        partner_params: Dict[str, Any],
        images_params: List[ImageParams],
        id_info_params: Dict[str, Any],
        options_params: OptionsParams,
    ) -> Dict[str, Any]:
        """Perform key/parameter validation, creates zipped file and uploads."""
        Utilities.validate_partner_params(partner_params)
        job_type = partner_params.get("job_type")

        if not id_info_params:
            if job_type in (
                JobType.ENHANCED_KYC,
                JobType.BASIC_KYC,
                JobType.BUSINESS_VERIFICATION,
            ):
                raise ValueError(
                    "id_info_params cannot be null or empty for job_type:"
                    f" {job_type}"
                )

            if job_type == JobType.BIOMETRIC_KYC:
                Utilities.validate_id_params(
                    self.url,
                    id_info_params,
                    partner_params,
                )
                id_info_params = {
                    "first_name": None,
                    "middle_name": None,
                    "last_name": None,
                    "country": None,
                    "id_type": None,
                    "id_number": None,
                    "dob": None,
                    "phone_number": None,
                    "entered": False,
                }

        if not options_params:
            options_params = OptionsParams(
                return_job_status=True,
                return_history=False,
                return_images=False,
                use_enrolled_image=False,
            )

        if (
            job_type == JobType.ENHANCED_KYC
            or job_type == JobType.BUSINESS_VERIFICATION
        ):
            return self.__call_id_api(
                partner_params,
                id_info_params,
                options_params,
            )

        if job_type == JobType.BUSINESS_VERIFICATION:
            return BusinessVerification(
                self.partner_id, self.api_key, self.sid_server
            ).submit_job(partner_params, id_info_params)

        self.__validate_options(options_params)
        validate_images(
            images_params,
            use_enrolled_image=options_params.get("use_enrolled_image", False),
            job_type=job_type,
        )
        Utilities.validate_id_params(self.url, id_info_params, partner_params)
        self.__validate_return_data(options_params)

        signature_params = self.signature_params
        use_enrolled_image = options_params.get("use_enrolled_image", False)
        prep_upload = WebApi.execute_http(
            f"{self.url}/upload",
            self.__prepare_prep_upload_payload(
                partner_params, signature_params, use_enrolled_image
            ),
        )
        if prep_upload.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/upload,"
                f" status={prep_upload.status_code},"
                f" response={prep_upload.json()}"
            )
        prep_upload_json_resp = prep_upload.json()
        upload_url: str = prep_upload_json_resp["upload_url"]
        smile_job_id: str = prep_upload_json_resp["smile_job_id"]
        zip_stream = generate_zip_file(
            partner_id=self.partner_id,
            callback_url=self.call_back_url,
            image_params=images_params,
            partner_params=partner_params,
            id_info_params=id_info_params,
            upload_url=upload_url,
            signature_params=signature_params,
        )

        upload_response = WebApi.upload(upload_url, zip_stream)
        if upload_response.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {upload_url},"
                f" status={upload_response.status_code},"
                f" response={upload_response.json()}"
            )

        if options_params["return_job_status"]:
            self.utilities = Utilities(
                self.partner_id, self.api_key, self.sid_server
            )
            job_status = self.poll_job_status(
                0, partner_params, options_params, signature_params
            )
            return job_status
        return {"success": True, "smile_job_id": smile_job_id}

    def get_web_token(
        self,
        user_id: str,
        job_id: str,
        product: str,
        timestamp: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create  authorization token used in Hosted Web Integration."""
        timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        callback_url = callback_url or self.call_back_url
        signature_params = Signature(
            self.partner_id, self.api_key
        ).generate_signature(timestamp)

        response = WebApi.execute_http(
            f"{self.url}/token",
            {
                "timestamp": signature_params["timestamp"],
                "signature": signature_params["signature"],
                "user_id": user_id,
                "job_id": job_id,
                "product": product,
                "callback_url": callback_url,
                "partner_id": self.partner_id,
            },
        )

        return dict(response.json())

    def __validate_options(self, options_params: OptionsParams) -> None:
        """Perform validations on options params and callback_url."""
        if not self.call_back_url and not options_params:
            raise ValueError(
                "Please choose to either get your response via the callback or"
                " job status query"
            )

        if options_params:
            for key in options_params:
                if key != "optional_callback" and not isinstance(
                    (options_params.get(key)), bool
                ):
                    raise ValueError(f"{key} needs to be a boolean")

    def __validate_return_data(self, options: OptionsParams) -> None:
        """Validate missing callback_url and option_params params."""
        if not self.call_back_url and not options["return_job_status"]:
            raise ValueError(
                "Please choose to either get your response via the callback or"
                " job status query"
            )

    def __prepare_prep_upload_payload(
        self,
        partner_params: Dict[str, str],
        signature_params: SignatureParams,
        use_enrolled_image: bool,
    ) -> Dict[str, Any]:
        """Validate signature params, returns expected upload payload.

        argument(s):
        partner_params: Dict containing all partner params
        Signature_params: Dict containing generated signature and timestamp
        use_enrolled_image: Performs validation based on boolean value
        option_params: Dict containing optional info params such as
            return_job_status, return_image_links, and return_history.
            Each of these keys has a boolean value
        """
        validate_signature_params(signature_params)

        return {
            "file_name": "selfie.zip",
            "smile_client_id": self.partner_id,
            "partner_params": partner_params,
            "model_parameters": {},
            "callback_url": self.call_back_url,
            "use_enrolled_image": use_enrolled_image,
            "source_sdk": "Python",
            "source_sdk_version": get_version(),
            **signature_params,
        }

    def poll_job_status(
        self,
        counter: int,
        partner_params: Dict[str, str],
        options_params: OptionsParams,
        signature_params: Optional[SignatureParams],
    ) -> Dict[str, Any]:
        """Get job status & check completion over some specified duration."""
        if signature_params is None:
            signature_params = get_signature(self.partner_id, self.api_key)

        validate_signature_params(signature_params)
        counter = counter + 1
        if counter < 4:
            time.sleep(2)
        else:
            time.sleep(4)
        if not isinstance(self.utilities, Utilities):
            raise ValueError("Utilities not initialized")
        job_status = self.utilities.get_job_status(
            partner_params, options_params, signature_params
        )

        if not job_status["job_complete"] and counter < 20:
            return self.poll_job_status(
                counter, partner_params, options_params, signature_params
            )

        return job_status

    @staticmethod
    def execute_http(url: str, payload: Dict[str, str]) -> Response:
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

    @staticmethod
    def upload(url: str, file: Any) -> Response:
        """Send a PUT request to upload file to specified url."""
        resp = requests.put(
            url=url, data=file, headers={"Content-type": "application/zip"}
        )
        return resp
