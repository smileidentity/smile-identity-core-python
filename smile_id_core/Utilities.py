import json
from typing import Dict

import requests

from smile_id_core.Signature import Signature
from smile_id_core.ServerError import ServerError

__all__ = ["Utilities", "get_signature", "validate_sec_params", "sid_server_map"]

sid_server_map = {
    0: "https://testapi.smileidentity.com/v1",
    1: "https://api.smileidentity.com/v1",
}


class Utilities:
    def __init__(self, partner_id, api_key, sid_server):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
        self.sid_server = sid_server
        if sid_server in [0, 1]:
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def get_job_status(self, partner_params, option_params, sec_params):
        if sec_params is None:
            sec_params = get_signature(
                self.partner_id, self.api_key, option_params.get("signature")
            )

        validate_sec_params(sec_params)
        Utilities.validate_partner_params(partner_params)
        if not option_params or option_params is None:
            options = {
                "return_job_status": True,
                "return_history": False,
                "return_images": False,
            }
        else:
            options = option_params
        return self.__query_job_status(
            partner_params.get("user_id"),
            partner_params.get("job_id"),
            options,
            sec_params,
        )

    def __query_job_status(self, user_id, job_id, option_params, sec_params):
        job_status = Utilities.execute_post(
            self.url + "/job_status",
            self.__configure_job_query(user_id, job_id, option_params, sec_params),
        )
        if job_status.status_code != 200:
            raise ServerError(
                "Failed to post entity to {}, response={}:{} - {}".format(
                    self.url + "/job_status",
                    job_status.status_code,
                    job_status.reason,
                    job_status.json(),
                )
            )
        else:
            job_status_json_resp = job_status.json()
            timestamp = job_status_json_resp["timestamp"]
            server_signature = job_status_json_resp["signature"]
            signature = Signature(self.partner_id, self.api_key)
            if option_params.get("signature"):
                valid = signature.confirm_signature(timestamp, server_signature)
            else:
                valid = signature.confirm_sec_key(timestamp, server_signature)
            if not valid:
                raise ServerError(
                    "Unable to confirm validity of the job_status response"
                )
            return job_status

    def __configure_job_query(self, user_id, job_id, options, sec_params):
        return {
            **sec_params,
            "partner_id": self.partner_id,
            "job_id": job_id,
            "user_id": user_id,
            "image_links": options["return_images"],
            "history": options["return_history"],
        }

    @staticmethod
    def validate_partner_params(partner_params):
        if not partner_params:
            raise ValueError("Please ensure that you send through partner params")

        if (
            not partner_params.get("user_id")
            or not partner_params.get("job_id")
            or not partner_params.get("job_type")
        ):
            raise ValueError("Partner Parameter Arguments may not be null or empty")

        if not isinstance(partner_params.get("user_id"), str):
            raise ValueError("Please ensure user_id is a string")

        if not isinstance(partner_params.get("job_id"), str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params.get("job_type"), int):
            raise ValueError("Please ensure job_type is a number")

    @staticmethod
    def validate_id_params(
        sid_server, id_info_params, partner_params, use_validation_api=False
    ):
        job_type = partner_params.get("job_type")
        if job_type != 6 and not id_info_params.get("entered"):
            return

        required_fields = ["country", "id_type"]
        if job_type != 6:
            required_fields += ["id_number"]

        for field in required_fields:
            if field in id_info_params:
                if id_info_params[field]:
                    continue
                else:
                    raise ValueError("key " + field + " cannot be empty")
            else:
                raise ValueError("key " + field + " cannot be empty")
        if not use_validation_api:
            return

        response = Utilities.get_smile_id_services(sid_server)
        if response.status_code != 200:
            raise ServerError(
                "Failed to get to {}, status={}, response={}".format(
                    "/services", response.status_code, response.json()
                )
            )
        response_json = response.json()
        if job_type == 6:
            doc_verification = response_json["hosted_web"]["doc_verification"]
            if not id_info_params["country"] in doc_verification:
                raise ValueError("country " + id_info_params["country"] + " is invalid")
            selected_country = doc_verification[id_info_params["country"]]["id_types"]
            if not id_info_params["id_type"] in selected_country:
                raise ValueError("id_type " + id_info_params["id_type"] + " is invalid")
        else:
            id_types_by_country = response_json["id_types"]
            if not id_info_params["country"] in id_types_by_country:
                raise ValueError("country " + id_info_params["country"] + " is invalid")
            selected_country = response_json["id_types"][id_info_params["country"]]
            if not id_info_params["id_type"] in selected_country:
                raise ValueError("id_type " + id_info_params["id_type"] + " is invalid")
            id_params = selected_country[id_info_params["id_type"]]
            for key in id_params:
                if key not in id_info_params and key not in partner_params:
                    raise ValueError("key " + key + " is required")
                if key in id_info_params and not id_info_params[key]:
                    raise ValueError("key " + key + " cannot be empty")
                if key in partner_params and not partner_params[key]:
                    raise ValueError("key " + key + " cannot be empty")

    @staticmethod
    def get_smile_id_services(sid_server):
        if sid_server in [0, 1]:
            url = sid_server_map[sid_server]
        else:
            url = sid_server
        response = Utilities.execute_get(url + "/services")
        if response.status_code != 200:
            raise ServerError(
                "Failed to get to {}, status={}, response={}".format(
                    url + "/services", response.status_code, response.json()
                )
            )
        return response

    @staticmethod
    def execute_get(url):
        resp = requests.get(
            url=url,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
            },
        )
        return resp

    @staticmethod
    def execute_post(url, payload):
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


def validate_sec_params(sec_key_dict: Dict):
    if not sec_key_dict.get("sec_key") and not sec_key_dict.get("signature"):
        raise Exception("Missing key, must provide a 'sec_key' or 'signature' field")
    if not sec_key_dict.get("timestamp"):
        raise Exception("Missing 'timestamp' field")


def get_signature(partner_id, api_key, is_signature):
    sec_key_gen = Signature(partner_id, api_key)
    sec_key_object = (
        sec_key_gen.generate_signature()
        if is_signature
        else sec_key_gen.generate_sec_key()
    )
    sec_key = sec_key_object.get("sec_key")
    signature = sec_key_object.get("signature")
    payload = {"timestamp": sec_key_object["timestamp"]}
    if sec_key:
        payload.update({"sec_key": sec_key})
    else:
        payload.update({"signature": signature})
    return payload
