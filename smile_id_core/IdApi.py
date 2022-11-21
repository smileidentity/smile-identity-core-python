import json
from typing import Dict, Optional, Union

import requests
from requests import Response

from smile_id_core.ServerError import ServerError
from smile_id_core.Utilities import (
    Utilities,
    get_signature,
    get_version,
    sid_server_map,
    validate_signature_params,
)

__all__ = ["IdApi"]


class IdApi:
    def __init__(self, partner_id: str, api_key: str, sid_server: Union[str, int]):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
        if sid_server in [0, 1, "0", "1"]:
            self.url = sid_server_map[int(sid_server)]
        else:
            self.url = str(sid_server)

    def submit_job(
        self,
        partner_params: Dict,
        id_params: Dict,
        use_validation_api=True,
        options_params: Optional[Dict] = None,
    ) -> Response:
        if not options_params:
            options_params = {}

        Utilities.validate_partner_params(partner_params)

        if not id_params:
            raise ValueError("Please ensure that you send through ID Information")

        Utilities.validate_id_params(
            self.url, id_params, partner_params, use_validation_api
        )

        if partner_params.get("job_type") != 5:
            raise ValueError(
                "Please ensure that you are setting your job_type to 5 to query ID Api"
            )

        signature_object = get_signature(self.partner_id, self.api_key)

        payload = self.__configure_json(partner_params, id_params, signature_object)
        response = self.__execute_http(payload)
        if response.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/id_verification, status={response.status_code}, response={response.json()}"
            )
        return response

    def __configure_json(
        self, partner_params: Dict, id_params: Dict, signature: Dict
    ) -> Dict:
        validate_signature_params(signature)
        return {
            **signature,
            "partner_id": self.partner_id,
            "partner_params": partner_params,
            "source_sdk": "Python",
            "source_sdk_version": get_version(),
            **id_params,
        }

    def __execute_http(self, payload: Dict) -> Response:
        data = json.dumps(payload)
        resp = requests.post(
            url=f"{self.url}/id_verification",
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json",
            },
        )
        return resp
