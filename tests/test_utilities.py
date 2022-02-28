import base64
import time

from uuid import uuid4

import pytest
import responses
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from smile_id_core import Signature, Utilities
from tests.stub_mixin import TestCaseWithStubs


class TestUtilities(TestCaseWithStubs):
    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.api_key = base64.b64encode(self.public_key).decode("UTF-8")
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.api_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())
        self.__reset_params()
        self.utilities = Utilities(self.partner_id, self.public_key, 0)

    def __reset_params(self):
        self.partner_params = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": 1,
        }
        self.partner_params_jt6 = {
            "user_id": str(uuid4()),
            "job_id": str(uuid4()),
            "job_type": 6,
        }
        self.id_info_params = {
            "first_name": "FirstName",
            "middle_name": "LastName",
            "last_name": "MiddleName",
            "country": "NG",
            "id_type": "PASSPORT",
            "id_number": "A00000000",
            "dob": "1989-09-20",
            "phone_number": "",
            "entered": True,
        }
        self.image_params = []
        self.image_params.append({"image_type_id": "2", "image": "base6image"})
        self.options_params = {
            "return_job_status": True,
            "return_history": True,
            "return_images": True,
        }

    def test_instance(self):
        self.assertEqual(self.utilities.partner_id, "001")
        self.assertEqual(self.utilities.api_key, self.public_key)
        self.assertEqual(
            self.utilities.url,
            "https://testapi.smileidentity.com/v1",
        )

    @staticmethod
    def _get_smile_services_response():
        return {
            "id_types": {
                "NG": {
                    "NIN": ["country", "id_type", "id_number", "user_id", "job_id"],
                    "CAC": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "company",
                        "job_id",
                    ],
                    "TIN": ["country", "id_type", "id_number", "user_id", "job_id"],
                    "VOTER_ID": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                    ],
                    "BVN": ["country", "id_type", "id_number", "user_id", "job_id"],
                    "PHONE_NUMBER": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                    ],
                    "DRIVERS_LICENSE": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob",
                    ],
                    "PASSPORT": [
                        "country",
                        "id_type",
                        "id_number",
                        "user_id",
                        "job_id",
                        "first_name",
                        "last_name",
                        "dob",
                    ],
                },
            },
            "hosted_web": {
                "doc_verification": {
                    "NG": {
                        "name": "Nigeria",
                        "id_types": {
                            "VOTER_ID": {"label": "Voter's ID"},
                            "NIN": {"label": "National ID"},
                            "PASSPORT": {"label": "Passport"},
                            "DRIVERS_LICENSE": {"label": "Driver's License"},
                        },
                    }
                },
            }

        }

    def test_no_partner_params(self):
        self.__reset_params()
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(None)
        self.assertEqual(
            ve.exception.args[0], "Please ensure that you send through partner params"
        )

    def test_missing_partner_params(self):
        self.__reset_params()
        self.partner_params["user_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        value_exception = ve.exception
        self.assertEqual(
            value_exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

        self.__reset_params()
        self.partner_params["job_id"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        self.assertEqual(
            ve.exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

        self.__reset_params()
        self.partner_params["job_type"] = None
        with self.assertRaises(ValueError) as ve:
            response = Utilities.validate_partner_params(self.partner_params)
        self.assertEqual(
            ve.exception.args[0],
            "Partner Parameter Arguments may not be null or empty",
        )

    @responses.activate
    def test_validate_id_params_should_raise_when_provided_with_invalid_input(self):
        self.__reset_params()

        self._stub_service("https://testapi.smileidentity.com/v1")
        self.id_info_params["country"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params
            )
        self.assertEqual(ve.exception.args[0], "key country cannot be empty")

        self.__reset_params()
        self.id_info_params["id_type"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params
            )
        self.assertEqual(ve.exception.args[0], "key id_type cannot be empty")

        self.__reset_params()
        self.id_info_params["id_number"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params
            )
        self.assertEqual(ve.exception.args[0], "key id_number cannot be empty")

        self.__reset_params()
        self.id_info_params["country"] = "ZW"
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "country ZW is invalid")

        self.__reset_params()
        self.id_info_params["id_type"] = "Not_Supported"
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "id_type Not_Supported is invalid")

        self.__reset_params()
        self.partner_params["user_id"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "key user_id cannot be empty")

        self.__reset_params()
        self.id_info_params["first_name"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "key first_name cannot be empty")

        self.__reset_params()
        self.partner_params.pop("user_id")
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "key user_id is required")

        # jt6 id pa

    @responses.activate
    def test_validate_id_params_should_raise_when_provided_with_invalid_input_for_jt6(self):
        self.__reset_params()

        self._stub_service("https://testapi.smileidentity.com/v1")
        self.id_info_params["country"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params_jt6
            )
        self.assertEqual(ve.exception.args[0], "key country cannot be empty")

        self.__reset_params()
        self.id_info_params["id_type"] = None
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params_jt6
            )
        self.assertEqual(ve.exception.args[0], "key id_type cannot be empty")

        self.__reset_params()
        self.id_info_params["id_number"] = None
        try:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params_jt6
            )
        except:
            pytest.fail("Unexpected MyError ..")

        self.__reset_params()
        self.id_info_params["country"] = "ZW"
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params_jt6, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "country ZW is invalid")

        self.__reset_params()
        self.id_info_params["id_type"] = "Not_Supported"
        with self.assertRaises(ValueError) as ve:
            Utilities.validate_id_params(
                self.utilities.url, self.id_info_params, self.partner_params_jt6, use_validation_api=True
            )
        self.assertEqual(ve.exception.args[0], "id_type Not_Supported is invalid")


    @responses.activate
    def test_get_job_status(self):
        self.__reset_params()
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=int(time.time()))
        self.stub_get_job_status(sec_timestamp, True)

        job_status = self.utilities.get_job_status(
            self.partner_params, self.options_params, sec_timestamp
        )
        body = {
            "sec_key": sec_timestamp["sec_key"],
            "timestamp": sec_timestamp["timestamp"],
            "partner_id": "001",
            "job_id": self.partner_params["job_id"],
            "user_id": self.partner_params["user_id"],
            "image_links": True,
            "history": True,
        }

        self.assertEqual(job_status.status_code, 200)
        self.assertIsNotNone(job_status.json())
        self.assert_request_called_with(
            "https://testapi.smileidentity.com/v1/job_status", responses.POST, body
        )

    @responses.activate
    def test_get_smile_id_services(self):
        self.__reset_params()

        self._stub_service("https://testapi.smileidentity.com/v1")
        self.utilities.get_smile_id_services(0)

        self._stub_service("https://api.smileidentity.com/v1")
        self.utilities.get_smile_id_services(1)

        self._stub_service("https://random-server.smileidentity.com/v1")
        job_status = self.utilities.get_smile_id_services(
            "https://random-server.smileidentity.com/v1"
        )

        self.assertEqual(job_status.status_code, 200)

    def _stub_service(self, url, json=None):
        if not json:
            json = TestUtilities._get_smile_services_response()

        responses.add(
            responses.GET,
            f"{url}/services",
            json=json,
        )
