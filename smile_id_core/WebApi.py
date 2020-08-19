import io
import json
import os
import time

import requests

from smile_id_core.IdApi import IdApi
from smile_id_core.Signature import Signature
from smile_id_core.Utilities import Utilities
from smile_id_core.ServerError import ServerError
import zipfile

__all__ = ['WebApi']


class WebApi:
    def __init__(self, partner_id, call_back_url, api_key, sid_server):
        if not partner_id or not api_key:
            raise ValueError("partner_id or api_key cannot be null or empty")
        self.partner_id = partner_id
        self.call_back_url = call_back_url
        self.api_key = api_key
        self.sid_server = sid_server
        self.utilities = None

        if sid_server in [0, 1]:
            sid_server_map = {
                0: "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def submit_job(self, partner_params, images_params,
                   id_info_params, options_params, use_validation_api=True):

        Utilities.validate_partner_params(partner_params)
        job_type = partner_params["job_type"]

        if not id_info_params:
            if job_type == 5:
                Utilities.validate_id_params(self.url, id_info_params, partner_params, use_validation_api)
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

        if job_type == 5:
            return self.__call_id_api(partner_params, id_info_params, use_validation_api)

        if not options_params:
            options_params = {
                "return_job_status": True,
                "return_history": False,
                "return_images": False,
            }

        self.__validate_options(options_params)
        self.validate_images(images_params)
        Utilities.validate_id_params(self.url, id_info_params, partner_params, use_validation_api)
        self.__validate_return_data(options_params)

        sec_key_object = self.__get_sec_key()

        prep_upload = WebApi.execute_http(self.url + "/upload",
                                          self.__prepare_prep_upload_payload(partner_params, sec_key_object["sec_key"],
                                                                             sec_key_object["timestamp"]))
        if prep_upload.status_code != 200:
            raise ServerError("Failed to post entity to {}, status={}, response={}".format(self.url + "/upload",
                                                                                            prep_upload.status_code,
                                                                                            prep_upload.json()))
        else:
            prep_upload_json_resp = prep_upload.json()
            upload_url = prep_upload_json_resp["upload_url"]
            smile_job_id = prep_upload_json_resp["smile_job_id"]
            info_json = self.__prepare_info_json(upload_url, partner_params, images_params, id_info_params,
                                                 sec_key_object["sec_key"], sec_key_object["timestamp"])
            zip_stream = WebApi.create_zip(info_json, images_params)
            upload_response = WebApi.upload(upload_url, zip_stream)
            if prep_upload.status_code != 200:
                raise ServerError("Failed to post entity to {}, status={}, response={}".format(upload_url,
                                                                                                prep_upload.status_code,
                                                                                                prep_upload.json()))

            if options_params["return_job_status"]:
                self.utilities = Utilities(self.partner_id, self.api_key, self.sid_server)
                job_status = self.poll_job_status(0, partner_params, options_params, sec_key_object["sec_key"],
                                                  sec_key_object["timestamp"])
                job_status_response = job_status.json()
                job_status_response["success"] = True
                job_status_response["smile_job_id"] = smile_job_id
                return job_status
            else:
                return {
                    "success": True,
                    "smile_job_id": smile_job_id
                }

    def __call_id_api(self, partner_params, id_info_params, use_validation_api):
        id_api = IdApi(self.partner_id, self.api_key, self.sid_server)
        return id_api.submit_job(partner_params, id_info_params, use_validation_api)

    @staticmethod
    def validate_images(images_params):
        if not images_params:
            raise ValueError("Please ensure that you send through image details")

        if not isinstance(images_params, list):
            raise ValueError("Please ensure that you send through image details as a list")

        if len(images_params) < 1:
            raise ValueError("Please ensure that you send through image details")

        for image in images_params:
            if image["image"].lower().endswith(('.png', '.jpg')):
                if not os.path.exists(image["image"]):
                    raise FileNotFoundError("No such file or directory %s" % (image["image"]))

    def __validate_options(self, options_params):
        if not self.call_back_url and not options_params:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query")

        if options_params:
            for key in options_params:
                if key != "optional_callback" and not type(options_params[key]) == bool:
                    raise ValueError(key + " needs to be a boolean")

    def __validate_return_data(self, options):
        if not self.call_back_url and not options["return_job_status"]:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query")

    def __get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    def __prepare_prep_upload_payload(self, partner_params, sec_key, timestamp):
        return {
            "file_name": "selfie.zip",
            "timestamp": timestamp,
            "sec_key": sec_key,
            "smile_client_id": self.partner_id,
            "partner_params": partner_params,
            "model_parameters": {},
            "callback_url": self.call_back_url,
        }

    def __prepare_info_json(self, upload_url, partner_params, image_params, id_info_params, sec_key, timestamp):
        return {
            "package_information": {
                "apiVersion": {
                    "buildNumber": 0,
                    "majorVersion": 2,
                    "minorVersion": 0,
                },
                "language": "python"
            },
            "misc_information": {
                "sec_key": sec_key,
                "retry": "false",
                "partner_params": partner_params,
                "timestamp": timestamp,
                "file_name": "selfie.zip",
                "smile_client_id": self.partner_id,
                "callback_url": self.call_back_url,
                "userData": {
                    "isVerifiedProcess": False,
                    "name": "",
                    "fbUserID": "",
                    "firstName": "Bill",
                    "lastName": "",
                    "gender": "",
                    "email": "",
                    "phone": "",
                    "countryCode": "+",
                    "countryName": ""
                }
            },
            "id_info": id_info_params,
            "images": WebApi.prepare_image_payload(image_params),
            "server_information": upload_url,
        }

    @staticmethod
    def prepare_image_payload(image_params):
        payload = []
        for image in image_params:
            if image["image"].lower().endswith(('.png', '.jpg', '.jpeg')):
                payload.append({
                    "image_type_id": image["image_type_id"],
                    "image": "",
                    "file_name": os.path.basename(image["image"]),
                })
            else:
                payload.append({
                    "image_type_id": image["image_type_id"],
                    "image": image["image"],
                    "file_name": "",
                })
        return payload

    @staticmethod
    def create_zip(info_json, image_params):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("info.json", data=json.dumps(info_json))
            for image in image_params:
                if image["image"].lower().endswith(('.png', '.jpg')):
                    zip_file.write(os.path.join(image["image"]), os.path.basename(image["image"]))
        return zip_buffer.getvalue()

    def poll_job_status(self, counter, partner_params, options_params, sec_key=None, timestamp=None):
        if sec_key is None:
            sec_key_object = self.__get_sec_key()
            sec_key = sec_key_object["sec_key"]
            timestamp = sec_key_object["timestamp"]

        counter = counter + 1
        if counter < 4:
            time.sleep(2)
        else:
            time.sleep(4)

        job_status = self.utilities.get_job_status(partner_params, options_params, sec_key, timestamp)
        job_status_response = job_status.json()
        if not job_status_response["job_complete"] and counter < 20:
            self.poll_job_status(counter, partner_params, options_params, sec_key, timestamp)

        return job_status

    @staticmethod
    def execute_http(url, payload):
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

    @staticmethod
    def upload(url, file):
        resp = requests.put(
            url=url,
            data=file,
            headers={
                "Content-type": "application/zip"
            })
        return resp
