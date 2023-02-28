"""Business verification kyc runnable example.

This works for both sandbox and production runs.

See https://docs.smileidentity.com/products/for-businesses-kyb/business-
verification for more information on business verification
"""

import os
import uuid

from smile_id_core.BusinessVerification import BusinessVerification
from smile_id_core.constants import JobType

# <Put your partner ID here>
partner_id: str = os.environ["PARTNER_ID"]
# <Put your default callback url here>
default_callback: str = os.environ["DEFAULT_CALLBACK"]
# You can download your API key from the Smile Identity portal.
# sandbox: 0 and production: 1
sid_server: str = os.environ["SID_SERVER"]  # 0 or 1
# <Put your base64 encoded API key here>
api_key: str = os.environ["API_KEY"]

connection = BusinessVerification(partner_id, api_key, sid_server)


""" Create required tracking parameters
Every communication between your server and the Smile Identity servers contain
these parameters. Use them to match up the job results with the job and user
you submitted."""

#  Create required tracking parameters
partner_params = {
    "job_id": f"job-{uuid.uuid4()}",  # your unique job_id
    "user_id": f"user-{uuid.uuid4()}",  # your unique user_id
    "job_type": JobType.BUSINESS_VERIFICATION,
}

"""The business incorporation type bn - business name, co - private/public
limited, it - incorporated trustees Only required for BASIC_BUSINESS_
REGISTRATION and BUSINESS_REGISTRATION in Nigeria Postal address of business.
Only Required for BUSINESS_REGISTRATION in Kenya"""

# Create ID number info
id_info = {
    "country": "NG",
    # <BASIC_BUSINESS_REGISTRATION | BUSINESS_REGISTRATION | TAX_INFORMATION>
    "id_type": "BUSINESS_REGISTRATION",
    "id_number": "0000000",  # <valid id number>
    "business_type": "co",  # NOTE: Only required for
    # `BASIC_BUSINESS_REGISTRATION` and `BUSINESS_REGISTRATION` in Nigeria (NG)
    "postal_address": "",  # NOTE: Only required for `BUSINESS_REGISTRATION`
    # in Kenya (KE)
    "postal_code": "",  # NOTE: Only required for `BUSINESS_REGISTRATION` in
    # Kenya (KE)
}


def submit_job() -> None:
    """Jobs are submitted to through the IdApi/BusinessVerification call.

    submit_job returns a response containing relevant information of the
    company is.
    """
    result = connection.submit_job(partner_params, id_info)
    print(result)


if __name__ == "__main__":
    submit_job()
