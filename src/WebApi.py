import json
import os
import time

import requests

from src import PartnerParameters, Options, ImageParameters, IDParameters
from src.IdApi import IdApi
from src.Signature import Signature
import zipfile

from src.Utilities import Utilities


class WebApi:
    def __init__(self, partner_id, call_back_url, api_key, sid_server):
        self.partner_id = partner_id
        self.call_back_url = call_back_url
        self.api_key = api_key
        self.sid_server = sid_server
        self.return_job_status = False
        self.return_history = False
        self.return_images = False
        self.partner_params = None
        self.image_params = None
        self.id_info_params = None
        self.options_params = None
        self.timestamp = 0
        self.sec_key = None
        self.utilities = None

        if sid_server in [0, 1]:
            sid_server_map = {
                0: "https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test",
                1: "https://la7am6gdm8.execute-api.us-west-2.amazonaws.com/prod",
            }
            self.url = sid_server_map[sid_server]
        else:
            self.url = sid_server

    def submit_job(self, partner_params: PartnerParameters, images_params: ImageParameters,
                   id_info_params: IDParameters, options_params: Options):

        self.validate_partner_params(partner_params)
        job_type = partner_params.get_params()["job_type"]

        if not id_info_params:
            if job_type == 5:
                self.validate_id_info_params(id_info_params)
            id_info_params = IDParameters(None, None, None, None, None,
                                          None,
                                          None,
                                          None,
                                          False)

        if job_type == 5:
            return self.__call_id_api(partner_params, id_info_params)

        if options_params:
            options = options_params.get_params()
            self.options_params = options_params
            self.return_job_status = options["return_job_status"]
            self.return_history = options["return_history"]
            self.return_images = options["return_images"]

        self.__validate_options(options_params)
        self.validate_images(images_params)
        self.validate_enrol_with_id(id_info_params)
        self.__validate_return_data()

        self.partner_params = partner_params
        self.image_params = images_params
        self.id_info_params = id_info_params

        sec_key_object = self.__get_sec_key()

        self.timestamp = sec_key_object["timestamp"]
        self.sec_key = sec_key_object["sec_key"]
        prep_upload = self.execute_http(self.url + "/upload", self.__prepare_prep_upload_payload())
        if prep_upload.status_code != 200:
            raise Exception("Failed to post entity to {}, response={}:{} - {}", self.url + "upload",
                            prep_upload.status_code,
                            prep_upload.reason, prep_upload.json())
        else:
            prep_upload_json_resp = prep_upload.json()
            upload_url = prep_upload_json_resp["upload_url"]
            smile_job_id = prep_upload_json_resp["smile_job_id"]
            info_json = self.__prepare_info_json(upload_url)
            zip_stream = self.__create_zip(info_json)
            upload_response = self.upload(upload_url, zip_stream)
            if prep_upload.status_code != 200:
                raise Exception("Failed to post entity to {}, response={}:{} - {}", self.url + "/upload",
                                upload_response.status_code,
                                upload_response.reason, upload_response.json())

            if self.return_job_status:
                self.utilities = Utilities(self.partner_id, self.api_key, self.sid_server)
                job_status = self.__poll_job_status(0)
                job_status_response = job_status.json()
                job_status_response["success"] = True
                job_status_response["smile_job_id"] = smile_job_id
                return job_status
            else:
                return {
                    "success": True,
                    "smile_job_id": smile_job_id
                }

    def __call_id_api(self, partner_params: PartnerParameters, id_info_params: IDParameters):
        id_api = IdApi(self.partner_id, self.api_key, self.sid_server)
        return id_api.submit_job(partner_params, id_info_params)

    @staticmethod
    def validate_partner_params(partner_params: PartnerParameters):
        if not partner_params:
            raise ValueError("Please ensure that you send through partner params")

        params = partner_params.get_params()
        if not params["user_id"] or not params["job_id"] or not params["job_type"]:
            raise ValueError("Partner Parameter Arguments may not be null or empty")

    @staticmethod
    def validate_id_info_params(id_params: IDParameters):
        if not id_params:
            raise ValueError("Please ensure that you send through partner params")

        for field in id_params.get_required_params():
            if field is None:
                raise ValueError(field + " cannot be empty")

    @staticmethod
    def validate_images(images_params: ImageParameters):
        if not images_params:
            raise ValueError("Please ensure that you send through image details")

        images = images_params.get_params()
        if len(images) < 1:
            raise ValueError("Please ensure that you send through image details")

    @staticmethod
    def validate_enrol_with_id(id_info_params: IDParameters):
        params = id_info_params.get_params()
        if params["entered"]:
            for field in id_info_params.get_required_params():
                if field in params:
                    if params[field]:
                        continue
                    else:
                        raise ValueError(field + " cannot be empty")
                else:
                    raise ValueError(field + " cannot be empty")

    def __validate_options(self, options_params: Options):
        if not self.call_back_url and not options_params:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query")

        if options_params:
            params = options_params.get_params()
            for key in params:
                if key != "optional_callback" and not type(params[key]) == bool:
                    raise ValueError(key + " needs to be a boolean")

    def __validate_return_data(self):
        if not self.call_back_url and not self.return_job_status:
            raise ValueError(
                "Please choose to either get your response via the callback or job status query")

    def __get_sec_key(self):
        sec_key_gen = Signature(self.partner_id, self.api_key)
        return sec_key_gen.generate_sec_key()

    def __prepare_prep_upload_payload(self):
        return {
            "file_name": "selfie.zip",
            "timestamp": self.timestamp,
            "sec_key": self.sec_key,
            "smile_client_id": self.partner_id,
            "partner_params": self.partner_params.get_params(),
            "model_parameters": {},
            "callback_url": self.call_back_url,
        }

    def __prepare_info_json(self, upload_url):
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
                "sec_key": self.sec_key,
                "retry": "false",
                "partner_params": self.partner_params.get_params(),
                "timestamp": self.timestamp,
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
            "id_info": self.id_info_params.get_params(),
            "images": self.__prepare_image_payload(),
            "server_information": upload_url,
        }

    def __prepare_image_payload(self):
        images = self.image_params.get_params()
        payload = []
        for image in images:
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

    def __create_zip(self, info_json):
        zip_file = zipfile.ZipFile("selfie.zip", 'w', zipfile.ZIP_DEFLATED)
        zip_file.writestr("info.json", data=json.dumps(info_json))
        images = self.image_params.get_params()
        for image in images:
            if image["image"].lower().endswith(('.png', '.jpg', '.jpeg')):
                zip_file.write(os.path.join(image["image"]), os.path.basename(image["image"]))
        zip_file.close()
        data = open(zip_file.filename, 'rb')
        return data

    def __poll_job_status(self, counter):
        counter = counter + 1
        if counter < 4:
            time.sleep(2)
        else:
            time.sleep(4)

        job_status = self.utilities.get_job_status(self.partner_params.get("user_id"),
                                                   self.partner_params.get("job_id"),
                                                   self.options_params)
        job_status_response = job_status.json()
        if not job_status_response["job_complete"] and counter < 20:
            self.__poll_job_status(counter)

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
