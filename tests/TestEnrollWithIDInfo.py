import os
import unittest
from uuid import uuid4

from src import PartnerParameters, IDParameters, WebApi, ImageParameters, Options

test_image_source = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_images/'))


class TestEnrollWithIDInfo(unittest.TestCase):

    def setUp(self):
        pass

    def test_enroll_no_selfie(self):
        pass
        # with self.assertRaises(ValueError) as ve:
        #     response = self.web_api.submit_job(self.partner_params, None,
        #                                        self.id_info_params, None)
        # value_exception = ve.exception
        # self.assertEqual(value_exception.args[0], u"You need to send through at least one selfie image")

    def test_enroll_without_options(self):
        pass
        # with self.assertRaises(ValueError) as ve:
        #     response = self.web_api.submit_job(self.partner_params, self.image_params,
        #                                        self.id_info_params, None)
        # value_exception = ve.exception
        # self.assertEqual(value_exception.args[0],
        #                  u"Please choose to either get your response via the callback or job status query")

    def test_enroll(self):
        pass
        # response = self.web_api.submit_job(self.partner_params, self.image_params,
        #                                    self.id_info_params, self.options_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["code"], u'2302')
