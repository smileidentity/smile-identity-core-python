"""The Enhanced KYC API allows you to query the Identity Information.

This queries for an individual using their ID number from one of our supported
ID Types. This API will return the personal information of the individual
found in the database of the ID authority.
See
https://docs.smileidentity.com/products/for-individuals-kyc/identity-lookup
for how to setup and retrieve configuration values for the IdApi class.
"""

import os
import uuid

from smile_id_core import IdApi

# Login to the Smile Identity portal to view your partner id.
partner_id: str = os.environ["PARTNER_ID"]
# Copy your API key from the Smile Identity portal.
api_key: str = os.environ["API_KEY"]
# '0':sandbox server, '1':production server.
sid_server: str = os.environ["SID_SERVER"]  # 0 or 1
default_callback = os.environ["DEFAULT_CALLBACK"]

connection = IdApi(partner_id, api_key, sid_server)

#  Create required tracking parameters
partner_params = {
    "job_id": f"job-{uuid.uuid4()}",  # your unique job_id
    "user_id": f"user-{uuid.uuid4()}",  # your unique user_id
    "job_type": 5,
}

# Create ID info
id_info = {
    "first_name": "FirstName",
    "last_name": "LastName",
    "country": "GH",  # <country code (2-letter)>
    "id_type": "PASSPORT",  # <id_type of document>
    "id_number": "G0000000",
    "dob": "2023/02/23",  # yyyy-mm-dd
    "phone_number": "true",  # true or false
}


def submit_job() -> None:
    """Submit job via the ID API."""

    result = connection.submit_job(partner_params, id_info)
    print(result)


if __name__ == "__main__":
    submit_job()
