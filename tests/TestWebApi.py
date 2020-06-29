import time
import unittest
from uuid import uuid4
from unittest.mock import patch

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from src import WebApi, PartnerParameters, IDParameters, ImageParameters, Options, Signature
from tests.TestEnrollWithIDInfo import test_image_source


class TestWebApi(unittest.TestCase):

    def setUp(self):
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.web_api = WebApi("001", 'https://a_callback.com', self.public_key, 0)
        self.partner_params = PartnerParameters(str(uuid4()), str(uuid4()), 1)
        self.id_info_params = IDParameters(u"FirstName", u"MiddleName", u"LastName", u"NG", u"PASSPORT",
                                           u"A00000000",
                                           u"1989-09-20",
                                           u"",
                                           True)
        self.image_params = ImageParameters()
        self.image_params.add(0, test_image_source + "/SID_Preview_Full.jpg")
        self.options_params = Options(None, True, True, True)
        self.key = RSA.generate(2048)
        self.public_key = self.key.publickey().export_key()
        self.partner_id = "001"
        self.signatureObj = Signature(self.partner_id, self.public_key)
        self.cipher = PKCS1_v1_5.new(self.key.exportKey())

    def test_instance(self):
        self.assertEqual(self.web_api.partner_id, "001")
        self.assertEqual(self.web_api.api_key, self.public_key)
        self.assertEqual(self.web_api.call_back_url, 'https://a_callback.com')
        self.assertEqual(self.web_api.url, 'https://3eydmgh10d.execute-api.us-west-2.amazonaws.com/test')

    def test_no_image_params(self):
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, None,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through image details")

    def test_no_partner_params(self):
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(None, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Please ensure that you send through partner params")

    def test_missing_partner_params(self):
        self.partner_params.add("user_id", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        value_exception = ve.exception
        self.assertEqual(value_exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.partner_params.add("user_id", str(uuid4()))
        self.partner_params.add("job_id", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

        self.partner_params.add("job_id", str(uuid4()))
        self.partner_params.add("job_type", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"Partner Parameter Arguments may not be null or empty")

    def test_id_info_params(self):
        self.id_info_params.add("country", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"country cannot be empty")

        self.id_info_params.add(u"country", u"NG")
        self.id_info_params.add(u"id_type", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"id_type cannot be empty")

        self.id_info_params.add(u"id_type", u"PASSPORT")
        self.id_info_params.add(u"id_number", None)
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0], u"id_number cannot be empty")

    # def test_non_required_options_params_jt5(self):
    #     self.partner_params.add("job_type", 5)
    #     with self.assertRaises(ValueError) as ve:
    #         response = self.web_api.submit_job(self.partner_params, self.image_params,
    #                                            self.id_info_params, None)
    #     self.assertEqual(ve.exception.args[0],
    #                      u"Please choose to either get your response via the callback or job status query")

    def test_boolean_options_params_non_jt5(self):
        self.options_params.add("return_job_status", "Test")
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0],
                         u"return_job_status needs to be a boolean")

        self.options_params.add("return_job_status", True)
        self.options_params.add("return_history", "tEST")
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0],
                         u"return_history needs to be a boolean")

        self.options_params.add("return_history", True)
        self.options_params.add("return_images", "tEST")
        with self.assertRaises(ValueError) as ve:
            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
        self.assertEqual(ve.exception.args[0],
                         u"return_images needs to be a boolean")

    def test_validate_return_data(self):
        timestamp = int(time.time())
        sec_timestamp = self.signatureObj.generate_sec_key(timestamp=timestamp)
        with patch('WebApi.requests.post') as mocked_post, patch('WebApi.requests.put') as mocked_put:
            mocked_post.return_value.status_code = 200
            mocked_post.return_value.ok = True
            mocked_post.return_value.text.return_value = {
                "upload_url": 'https://some_url.com',
                "smile_job_id": "1",
                "timestamp": sec_timestamp["timestamp"],
                "signature": sec_timestamp["sec_key"],
                "job_complete": True
            }
            mocked_post.return_value.json.return_value = {
                "upload_url": 'https://some_url.com',
                "smile_job_id": "1",
                "timestamp": sec_timestamp["timestamp"],
                "signature": sec_timestamp["sec_key"],
                "job_complete": True
            }

            mocked_put.return_value.status_code = 200
            mocked_put.return_value.ok = True

            response = self.web_api.submit_job(self.partner_params, self.image_params,
                                               self.id_info_params, self.options_params)
