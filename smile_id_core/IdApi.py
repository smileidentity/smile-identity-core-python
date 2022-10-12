import json
import typing

import requests

from smile_id_core.ServerError import ServerError
from smile_id_core.Utilities import get_signature
from smile_id_core.Utilities import sid_server_map
from smile_id_core.Utilities import Utilities
from smile_id_core.Utilities import validate_sec_params

__all__ = ["IdApi"]


class IdApi:
    def __init__(self, partner_id: str, api_key: str, sid_server: typing.Union[str, int]):
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
        partner_params: typing.Dict,
        id_params: typing.Dict,
        use_validation_api=True,
        options_params: typing.Dict = None,
    ):
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

        sec_key_object = get_signature(self.partner_id, self.api_key)
        payload = self.__configure_json(partner_params, id_params, sec_key_object)
        response = self.__execute_http(payload)
        if response.status_code != 200:
            raise ServerError(
                f"Failed to post entity to {self.url}/id_verification, status={response.status_code}, response={response.json()}"
            )
        return response

    def __configure_json(self, partner_params, id_params, sec_key):
        validate_sec_params(sec_key)
        payload = {
            **sec_key,
            "partner_id": self.partner_id,
            "partner_params": partner_params,
            "source_sdk": "Python",
            "source_sdk_version": "2.0.0",
        }
        payload.update(id_params)
        return payload

    def __execute_http(self, payload):
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
