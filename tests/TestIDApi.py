import os
import time
import unittest
from uuid import uuid4
from unittest.mock import patch

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from src import WebApi, PartnerParameters, IDParameters, ImageParameters, Options, Signature, IdApi


class TestIdApi(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.id_api = IdApi("001", self.public_key, 0)
        self.partner_params = PartnerParameters(str(uuid4()), str(uuid4()), 5)
        self.id_info_params = IDParameters(u"FirstName", u"MiddleName", u"LastName", u"NG", u"PASSPORT",
                                           u"A00000000",
                                           u"1989-09-20",
                                           u"",
                                           True)

        self.options_params = Options(None, True, True, True)
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

    def test_instance(self):
        self.assertEqual(self.id_api.partner_id, "001")
        self.assertEqual(self.id_api.api_key, self.public_key)
        self.assertEqual(self.id_api.url, 'https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test')

    def test_no_partner_params(self):
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(None, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through partner params")

    def test_no_id_info_params(self):
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, None)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through ID Information")

    def test_invalid_job_type(self):
        self.partner_params.add("job_type", 0)
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you are setting your job_type to 5 to query ID Api")

    def test_id_info_params(self):
        self.id_info_params.add("country", None)
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"country cannot be empty")

        self.id_info_params.add(u"country", u"NG")
        self.id_info_params.add(u"id_type", None)
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"id_type cannot be empty")

        self.id_info_params.add(u"id_type", u"PASSPORT")
        self.id_info_params.add(u"id_number", None)
        with self.assertRaises(ValueError) as ve:
            response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        self.assertEqual(ve.exception.args[0], u"id_number cannot be empty")

    def get_id_response(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        return {"JSONVersion": "1.0.0",
                "SmileJobID": "0000000324",
                "PartnerParams": {
                    "job_id": "D7t4PtgWk9kl",
                    "user_id": "fffafbdc-073f-44b1-81f5-588866124ae2",
                    "job_type": 5
                },
                "ResultType": "ID Verification",
                "ResultText": "ID Number Validated",
                "ResultCode": "1012",
                "IsFinalResult": "true",
                "Actions": {
                    "Verify_ID_Number": "Verified",
                    "Return_Personal_Info": "Returned"
                },
                "Country": "NG",
                "IDType": "PASSPORT",
                "IDNumber": "A00000000",
                "ExpirationDate": "2024-02-13",
                "FullName": "DOE LEO JOE",
                "DOB": "2000-09-20",
                "Photo": "/9j/4AAQSAAAAAD//gASSVJJP/bAEMABAMDAw/wCUUP/Z",
                "PhoneNumber": "Not Available",
                "Gender": "Male",
                "Address": "Not Available",
                "FullData":
                    {

                    },
                "Source": "ID API",
                "timestamp": timestamp,
                "signature": sec_timestamp["sec_key"]
                }

    def test_validate_return_data(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        with patch('requests.post') as mocked_post:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = self.get_id_response()
            mocked_post.return_value.json.return_value = self.get_id_response()

            response = self.id_api.submit_job(self.partner_params, self.id_info_params)

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.json())
