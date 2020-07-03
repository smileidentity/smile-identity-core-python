import json

import requests

from src.Signature import Signature


class Utilities:
    def __init__(self, partner_id, api_key, sid_server):
        self.partner_id = partner_id
        self.api_key = api_key
        self.sid_server = sid_server
        if sid_server in [0, 1]:
            sid_server_map = {
                0: "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def get_job_status(self, partner_params, option_params, sec_key, timestamp):

        Utilities.validate_partner_params(partner_params)
        if not option_params or option_params is None:
            options = {
                "return_job_status": True,
                "return_history": False,
                "return_images": False,
            }
        else:
            options = option_params
        return self.__query_job_status(partner_params.get("user_id"), partner_params.get("job_id"), options, sec_key,
                                       timestamp)

    def __query_job_status(self, user_id, job_id, option_params, sec_key, timestamp):
        job_status = self.execute(self.url + "/job_status",
                                  self.__configure_job_query(user_id, job_id, option_params, sec_key, timestamp))
        if job_status.status_code != 200:
            raise Exception("Failed to post entity to {}, response={}:{} - {}", self.url + "/job_status",
                            job_status.status_code,
                            job_status.reason, job_status.json())
        else:
            job_status_json_resp = job_status.json()
            timestamp = job_status_json_resp["timestamp"]
            server_signature = job_status_json_resp["signature"]
            signature = Signature(self.partner_id, self.api_key)
            valid = signature.confirm_sec_key(timestamp, server_signature)
            if not valid:
                raise Exception("Unable to confirm validity of the job_status response")
            return job_status

    def __configure_job_query(self, user_id, job_id, options, sec_key, timestamp):
        return {
            "sec_key": sec_key,
            "timestamp": timestamp,
            "partner_id": self.partner_id,
            "job_id": job_id,
            "user_id": user_id,
            "image_links": options["return_images"],
            "history": options["return_history"],
        }

    def __get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    @staticmethod
    def validate_partner_params(partner_params):
        if not partner_params:
            raise ValueError("Please ensure that you send through partner params")

        if not partner_params["user_id"] or not partner_params["job_id"] or not partner_params["job_type"]:
            raise ValueError("Partner Parameter Arguments may not be null or empty")

        if not isinstance(partner_params["user_id"], str):
            raise ValueError("Please ensure user_id is a string")

        if not isinstance(partner_params["job_id"], str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params["job_id"], str):
            raise ValueError("Please ensure job_id is a string")

        if not isinstance(partner_params["job_type"], int):
            raise ValueError("Please ensure job_id is a number")

    @staticmethod
    def validate_id_params(id_info_params):
        if id_info_params["entered"]:
            for field in ["country", "id_type", "id_number"]:
                if field in id_info_params:
                    if id_info_params[field]:
                        continue
                    else:
                        raise ValueError(field + " cannot be empty")
                else:
                    raise ValueError(field + " cannot be empty")

    @staticmethod
    def execute(url, payload):
        data = json.dumps(payload)
        resp = requests.post(
            url=url,
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json"
            })
        return resp
