import unittest
from uuid import uuid4

from src import WebApi, PartnerParameters, IDParameters, ImageParameters, Options
from tests.TestEnrollWithIDInfo import test_image_source


class TestUpdatePhoto(unittest.TestCase):

    def setUp(self):
        pass

    def test_update_photo(self):
        pass
        # response = self.web_api.submit_job(self.partner_params, self.image_params,
        #                                    None, self.options_params)
        # response_json = response.json()
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response_json["code"], u'2302')
