import http.client
import json
import IDParameters
import PartnerParameters
import SIDServer
from Signature import Signature


class IDApi:
    timestamp = 0
    sec_key = ""

    def __init__(self, partner_id, api_key, sid_server=SIDServer.TEST):
        if not partner_id or not api_key:
            raise Exception("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.api_key = api_key
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
        response = self.execute(payload)
        return response

    def get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    def configure_json(self, partner_params: PartnerParameters, id_params: IDParameters):
        payload = {
            "sec_key": self.sec_key,
            "timestamp": self.timestamp,
            "partner_id": self.partner_id,
            "partner_params": partner_params,
        }
        payload.update(id_params)
        return payload

    def execute(self, payload):
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Content-type": "application/json"
        }
        conn = http.client.HTTPConnection(self.url)
        conn.request("POST", "", json.dumps(payload), headers)
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()
        return data
