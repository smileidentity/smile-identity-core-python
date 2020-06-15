import http.client
import json

import Options
from Signature import Signature


class Utilities:
    def __init__(self, partner_id, call_back_url, api_key, sid_server):
        self.partner_id = partner_id
        self.call_back_url = call_back_url
        self.api_key = api_key
        self.sid_server = sid_server
        self.timestamp = 0
        self.sec_key = None
        if sid_server in [0, 1]:
            sid_server_map = {
                0: "3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def get_job_status(self, user_id, job_id, option_params: Options):
        sec_key_object = self.get_sec_key()

        self.timestamp = sec_key_object["timestamp"]
        self.sec_key = sec_key_object["sec_key"]

        if not option_params or option_params is None:
            options = {
                "return_history": False,
                "return_images": False
            }
        else:
            options = option_params

        return self.query_job_status(user_id, job_id, options)

    def query_job_status(self, user_id, job_id, option_params):
        job_status = self.execute(self.url + "/job_status", self.configure_job_query(user_id, job_id, option_params))
        if job_status.status is not 200:
            raise Exception("Failed to post entity to {}, response={}:{} - {}", self.url + "/job_status",
                            job_status.status,
                            job_status.reason, job_status.read)
        else:
            job_status_json_resp = json.loads(job_status.read)
            timestamp = job_status_json_resp["timestamp"]
            server_signature = job_status_json_resp["signature"]
            signature = Signature(self.partner_id, self.api_key)
            valid = signature.confirm_sec_key(timestamp, server_signature)
            if not valid:
                raise Exception("Unable to confirm validity of the job_status response")
            return job_status_json_resp

    def configure_job_query(self, user_id, job_id, options):
        return {
            "sec_key": self.sec_key,
            "timestamp": self.timestamp,
            "partner_id": self.partner_id,
            "job_id": job_id,
            "user_id": user_id,
            "image_links": options["return_images"],
            "history": options["return_history"],
        }

    def get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    @staticmethod
    def execute(url, payload):
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Content-type": "application/json"
        }
        conn = http.client.HTTPConnection(url)
        conn.request("POST", "", json.dumps(payload), headers)
        return conn.getresponse()
