import unittest
from uuid import uuid4

from src import WebApi, PartnerParameters, ImageParameters, Options
from src.IDApi import IDApi
from tests.TestEnrollWithIDInfo import test_image_source


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        pass
        # self.api_key = u"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnlG24VNQIbD8LMmHRwHsQWzO1
        #                               q1b+ymJDyiVrpch+av9ermS/njWzo1wpUg7jOX5vc7utF/nJCmekUDr4vXPz1dfX
        #                               HDnyYtBnlleBTtYKwipwLzDj0PO7aGX7rz/ebkHcS/PdlP+prLFw584qcesnq4rQ
        #                               n64nLz7y0BE/RCDQAwIDAQAB"""
        # self.partner_id = "210"
        # self.web_api = WebApi("210", None, self.api_key, 0)
        # self.partner_params = PartnerParameters("bff67535-cbcd-4db5-b2eb-cedbfee53aa4", str(uuid4()), 2)
        # self.image_params = ImageParameters()
        # self.image_params.add(0, test_image_source + "/SID_Preview_Full.jpg")
        # self.options_params = Options(None, True, True, True)

    def test_auth(self):
        pass
        # response = self.web_api.submit_job(self.partner_params, self.image_params,
        #                                    None, self.options_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["code"], u'2302')
