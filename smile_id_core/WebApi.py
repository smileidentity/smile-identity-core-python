import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from requests import Response

from smile_id_core.IdApi import IdApi
from smile_id_core.image_upload import generate_zip_file, validate_images
from smile_id_core.ServerError import ServerError
from smile_id_core.Signature import Signature
from smile_id_core.Utilities import (
    Utilities,
    get_signature,
    get_version,
    sid_server_map,
    validate_signature_params,
)

__all__ = ["WebApi"]


class WebApi:
    def __init__(
        self,
        partner_id: str,
        call_back_url: str,
        api_key: str,
        sid_server: Union[str, int],
    ):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.call_back_url = call_back_url
        self.api_key = api_key
        self.sid_server = sid_server
        self.utilities: Optional[Utilities] = None

        if sid_server in [0, 1, "0", "1"]:
            self.url = sid_server_map[int(sid_server)]
        else:
            self.url = str(sid_server)

    def submit_job(
        self,
        partner_params: Dict,
        images_params: List[Dict],
        id_info_params: Dict,
        options_params: Dict,
        use_validation_api=True,
    ) -> Union[Response, Dict]:

        Utilities.validate_partner_params(partner_params)
        job_type = partner_params.get("job_type")

        if not id_info_params:
            if job_type == 5:
                Utilities.validate_id_params(
                    self.url, id_info_params, partner_params, use_validation_api
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
            options_params = {
                "return_job_status": True,
                "return_history": False,
                "return_images": False,
            }

        if job_type == 5:
            return self.__call_id_api(
                partner_params, id_info_params, use_validation_api, options_params
            )

        self.__validate_options(options_params)
        validate_images(
            images_params,
            use_enrolled_image=options_params.get("use_enrolled_image", False),
            job_type=job_type,
        )
        Utilities.validate_id_params(
            self.url, id_info_params, partner_params, use_validation_api
        )
        self.__validate_return_data(options_params)

        signature_params = get_signature(self.partner_id, self.api_key)
        use_enrolled_image = options_params.get("use_enrolled_image", False)
        prep_upload = WebApi.execute_http(
            f"{self.url}/upload",
            self.__prepare_prep_upload_payload(
                partner_params, signature_params, use_enrolled_image
            ),
        )
        if prep_upload.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/upload, status={prep_upload.status_code}, response={prep_upload.json()}"
            )
        else:
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
                    f"Failed to post entity to {upload_url}, status={upload_response.status_code}, response={upload_response.json()}"
                )

            if options_params["return_job_status"]:
                self.utilities = Utilities(
                    self.partner_id, self.api_key, self.sid_server
                )
                job_status = self.poll_job_status(
                    0, partner_params, options_params, signature_params
                )
                return job_status
            else:
                return {"success": True, "smile_job_id": smile_job_id}

    def get_web_token(
        self,
        user_id: str,
        job_id: str,
        product: str,
        timestamp: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Response:

        timestamp = timestamp or datetime.now().isoformat()
        callback_url = callback_url or self.call_back_url
        signature_params = Signature(self.partner_id, self.api_key).generate_signature(
            timestamp
        )

        return WebApi.execute_http(
            f"{self.url}/token",
            {
                **signature_params,
                "user_id": user_id,
                "job_id": job_id,
                "product": product,
                "callback_url": callback_url,
                "partner_id": self.partner_id,
            },
        )

    def __call_id_api(
        self,
        partner_params: Dict,
        id_info_params: Dict,
        use_validation_api: bool,
        options_params: Dict,
    ) -> Response:
        id_api = IdApi(self.partner_id, self.api_key, self.sid_server)
        return id_api.submit_job(
            partner_params, id_info_params, use_validation_api, options_params
        )

    def __validate_options(self, options_params: Dict) -> None:
        if not self.call_back_url and not options_params:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query"
            )

        if options_params:
            for key in options_params:
                if key != "optional_callback" and not type(options_params[key]) == bool:
                    raise ValueError(f"{key} needs to be a boolean")

    def __validate_return_data(self, options: Dict) -> None:
        if not self.call_back_url and not options["return_job_status"]:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query"
            )

    def __prepare_prep_upload_payload(
        self, partner_params: Dict, signature_params: Dict, use_enrolled_image: bool
    ) -> Dict:
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
        partner_params: Dict,
        options_params: Dict,
        signature_params: Optional[Dict],
    ) -> Response:
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
        job_status_response = job_status.json()
        if not job_status_response["job_complete"] and counter < 20:
            return self.poll_job_status(
                counter, partner_params, options_params, signature_params
            )

        return job_status

    @staticmethod
    def execute_http(url: str, payload: Dict) -> Response:
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
        resp = requests.put(
            url=url, data=file, headers={"Content-type": "application/zip"}
        )
        return resp
