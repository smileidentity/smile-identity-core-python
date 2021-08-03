import json
import unittest
from typing import Dict

import responses


class TestCaseWithStubs(
    unittest.TestCase,
):
    def stub_get_job_status(self, sec_key, job_complete=True, with_error=None):
        if with_error:
            job_status_response = {
                "status": 400,
                "json": {"code": "2098", "error": with_error},
            }
        else:
            job_status_response = {
                "status": 200,
                "json": self._get_job_status_response(sec_key, job_complete),
            }

        responses.add(
            responses.POST,
            "https://testapi.smileidentity.com/v1/job_status",
            **job_status_response,
        )
        return job_status_response["json"]

    def _get_job_status_response(self, sec_key, job_complete=True):
        return {
            "signature": sec_key.get("signature") or sec_key.get("sec_key"),
            "timestamp": sec_key.get("timestamp"),
            "job_complete": job_complete,
            "job_success": True,
            "result": {
                "ResultText": "Enroll User",
                "ResultType": "SAIA",
                "SmileJobID": "0000001897",
                "JSONVersion": "1.0.0",
                "IsFinalResult": "true",
                "PartnerParams": {
                    "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                    "user_id": "e54e0e98-8b8c-4215-89f5-7f9ea42bf650",
                    "job_type": 4,
                },
                "ConfidenceValue": "100",
                "IsMachineResult": "true",
            },
            "image_links": {
                "selfie_image": "https://smile-fr-results.s3.us-west-2.amazonaws.com/test/000000/023/023-0000001897-LoRSpxJUzmYgYS2R00XpaHJYLOiNXN/SID_Preview_FULL.jpg"
            },
            "code": "2302",
            "history": [
                {
                    "ResultCode": "1210",
                    "ResultText": "Enroll User",
                    "ResultType": "DIVA",
                    "SmileJobID": "0000000857",
                    "JSONVersion": "1.0.0",
                    "IsFinalResult": "true",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                    },
                },
                {
                    "ResultCode": "0814",
                    "ResultText": "Provisional Enroll - Under Review",
                    "SmileJobID": "0000000857",
                    "ConfidenceValue": "97.000000",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                    },
                },
                {
                    "DOB": "1990-01-01",
                    "IDType": "BVN",
                    "Country": "Nigeria",
                    "FullName": "Peter Parker",
                    "ExpirationDate": "Not Available",
                    "IDNumber": "A01234567",
                    "ResultCode": "1012",
                    "ResultText": "ID Validated",
                    "ResultType": "ID Verification",
                    "SmileJobID": "0000000857",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                        "ExpirationDate": "Not Available",
                    },
                },
            ],
        }

    def _get_pre_upload_response(self, sec_key: Dict):
        return {
            "signature": sec_key.get("signature") or sec_key.get("sec_key"),
            "timestamp": sec_key.get("timestamp"),
            "upload_url": "https://some_url.com",
            "smile_job_id": "0000000857",
            "job_complete": True,
            "job_success": True,
            "result": {
                "ResultText": "Enroll User",
                "ResultType": "SAIA",
                "SmileJobID": "0000001897",
                "JSONVersion": "1.0.0",
                "IsFinalResult": "true",
                "PartnerParams": {
                    "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                    "user_id": "e54e0e98-8b8c-4215-89f5-7f9ea42bf650",
                    "job_type": 4,
                },
                "ConfidenceValue": "100",
                "IsMachineResult": "true",
            },
            "image_links": {
                "selfie_image": "https://smile-fr-results.s3.us-west-2.amazonaws.com/test/000000/023/023-0000001897-LoRSpxJUzmYgYS2R00XpaHJYLOiNXN/SID_Preview_FULL.jpg"
            },
            "code": "2302",
            "history": [
                {
                    "ResultCode": "1210",
                    "ResultText": "Enroll User",
                    "ResultType": "DIVA",
                    "SmileJobID": "0000000857",
                    "JSONVersion": "1.0.0",
                    "IsFinalResult": "true",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                    },
                },
                {
                    "ResultCode": "0814",
                    "ResultText": "Provisional Enroll - Under Review",
                    "SmileJobID": "0000000857",
                    "ConfidenceValue": "97.000000",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                    },
                },
                {
                    "DOB": "1990-01-01",
                    "IDType": "BVN",
                    "Country": "Nigeria",
                    "FullName": "Peter Parker",
                    "ExpirationDate": "Not Available",
                    "IDNumber": "A01234567",
                    "ResultCode": "1012",
                    "ResultText": "ID Validated",
                    "ResultType": "ID Verification",
                    "SmileJobID": "0000000857",
                    "PartnerParams": {
                        "job_id": "52d0de86-be3b-4219-9e96-8195b0018944",
                        "user_id": "1511bf02-801a-4b57-ac8e-ef17e26bfeb4",
                        "job_type": "1",
                        "optional_info": "Partner can put whatever they want as long as it is a string",
                        "more_optional_info": "There can be as much or as little or no optional info",
                        "ExpirationDate": "Not Available",
                    },
                },
            ],
        }

    def stub_upload_request(self, sec_key, fail_with_message=None):
        post_response = self._get_pre_upload_response(sec_key)
        responses.add(
            responses.POST,
            "https://testapi.smileidentity.com/v1/upload",
            status=200,
            json=post_response,
        )
        upload_response = {"status": 200, "json": {}}
        if fail_with_message:
            upload_response = {
                "status": 400,
                "json": {"code": "2205", "error": fail_with_message},
            }
        responses.add(responses.PUT, post_response["upload_url"], **upload_response)
        return post_response

    def assert_request_called_with(self, url, method, body):
        called_requests = [
            call.request
            for call in responses.calls
            if call.request.url == url and call.request.method == method
        ]
        size = len(called_requests)
        if size == 0:
            self.fail(f"{method} {url} not called")
        # elif size == 1:
        #     self.assertEqual(called_requests[0].body, json.dumps(body))
        else:
            found = False
            for request in called_requests:
                try:
                    self.assertEqual(request.body, json.dumps(body))
                    found = True
                except AssertionError as e:
                    pass
            if not found:
                self.fail(f"No request match call with body {body}")
