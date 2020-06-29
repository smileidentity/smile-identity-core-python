import unittest
from unittest.mock import patch
from Crypto.PublicKey import RSA

from src import IDApi, PartnerParameters, IDParameters, WebApi


class TestIDValidation(unittest.TestCase):

    def setUp(self):
        pass
        # self.api_key = u"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnlG24VNQIbD8LMmHRwHsQWzO1
        #                 q1b+ymJDyiVrpch+av9ermS/njWzo1wpUg7jOX5vc7utF/nJCmekUDr4vXPz1dfX
        #                 HDnyYtBnlleBTtYKwipwLzDj0PO7aGX7rz/ebkHcS/PdlP+prLFw584qcesnq4rQ
        #                 n64nLz7y0BE/RCDQAwIDAQAB"""
        # self.partner_id = "210"
        # self.id_api = IDApi("210", self.api_key, 0)
        # self.web_api = WebApi("210", None, self.api_key, 0)
        # self.partner_params = PartnerParameters("xBAdAAABBAMBAQAAAAsAAAAAAAAFAg", "eBAddAABBAMBAQAAAAAAAAAAAAAFAg", 5)
        # self.id_info_params = IDParameters(u"FirstName", u"MiddleName", u"LastName", u"NG", u"PASSPORT",
        #                                    u"A00000000",
        #                                    u"1989-09-20",
        #                                    u"",
        #                                    True)

    def test_correct_id_api(self):
        pass
        # response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["ResultCode"], u"1012")

    def test_correct_web_api(self):
        pass
        # response = self.web_api.submit_job(self.partner_params, None,
        #                                    self.id_info_params, None)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["ResultCode"], u"1012")

    def test_in_correct_id_api(self):
        pass
        # self.id_info_params.add("id_number", u"A00000001")
        # response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["ResultCode"], u'1013')

    def test_incorrect_metadata_id_api(self):
        pass
        # self.id_info_params.add("id_number", u"A00000002")
        # response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["ResultCode"], u'1012')

    def test_unknown_issue_id_api(self):
        pass
        # self.id_info_params.add("id_number", u"A00000003")
        # response = self.id_api.submit_job(self.partner_params, self.id_info_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["ResultCode"], u'1015')
