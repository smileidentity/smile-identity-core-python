import http.client
import json
from .PartnerParameters import PartnerParameters
from .IDParameters import IDParameters
from src.Signature import Signature
import requests


class IDApi:
    timestamp = 0
    sec_key = ""

    def __init__(self, partner_id, api_key, sid_server):
        if not partner_id or not api_key:
            raise Exception("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
        if sid_server in [0, 1]:
            sid_server_map = {
                0: "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def submit_job(self, partner_params: PartnerParameters, id_params: IDParameters):
        if not isinstance(partner_params, PartnerParameters):
            raise TypeError("partner_params must be of type PartnerParameters")

        if not isinstance(id_params, IDParameters):
            raise TypeError("id_params must be of type IDParameters")

        if partner_params.get("job_type") != 5:
            raise ValueError("Please ensure that you are setting your job_type to 5 to query ID Api")

        sec_key_object = self.get_sec_key()
        self.timestamp = sec_key_object["timestamp"]
        self.sec_key = sec_key_object["sec_key"]
        payload = self.configure_json(partner_params, id_params)
        response = self.execute_http(payload)
        return response

    def get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    def configure_json(self, partner_params: PartnerParameters, id_params: IDParameters):
        payload = {
            "sec_key": self.sec_key,
            "timestamp": self.timestamp,
            "partner_id": self.partner_id,
            "partner_params": partner_params.get_params(),
        }
        payload.update(id_params.get_params())
        return payload

    def execute_http(self, payload):
        data = json.dumps(payload)
        resp = requests.post(
            url=self.url + "/id_verification",
            data=data,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Content-type": "application/json"
            })
        return resp
