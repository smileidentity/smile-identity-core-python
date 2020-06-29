import os
import unittest
from uuid import uuid4

from src import PartnerParameters, IDParameters, WebApi, ImageParameters, Options

test_image_source = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_images/'))


class TestEnrollWithIDInfo(unittest.TestCase):

    def setUp(self):
        pass
        # self.api_key = u"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnlG24VNQIbD8LMmHRwHsQWzO1
        #                    q1b+ymJDyiVrpch+av9ermS/njWzo1wpUg7jOX5vc7utF/nJCmekUDr4vXPz1dfX
        #                    HDnyYtBnlleBTtYKwipwLzDj0PO7aGX7rz/ebkHcS/PdlP+prLFw584qcesnq4rQ
        #                    n64nLz7y0BE/RCDQAwIDAQAB"""
        # self.partner_id = "210"
        # self.web_api = WebApi("210", None, self.api_key, 0)
        # self.partner_params = PartnerParameters(str(uuid4()), str(uuid4()), 1)
        # self.id_info_params = IDParameters(u"FirstName", u"MiddleName", u"LastName", u"NG", u"PASSPORT",
        #                                    u"A00000000",
        #                                    u"1989-09-20",
        #                                    u"",
        #                                    True)
        # self.image_params = ImageParameters()
        # self.image_params.add(0, test_image_source + "/SID_Preview_Full.jpg")
        # self.options_params = Options(None, True, True, True)

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
