"""Smart-selfie registration that runs anti-spoof before registring the selfie.

See https://docs.usesmileid.com/integration-options/server-to-server/python/products/smartselfie-tm-authentication
for how to setup and retrieve configuration values for the
WebApi class.
"""

import base64
import os
import uuid
from typing import List

from smile_id_core import WebApi
from smile_id_core.constants import ImageTypes, JobType
from smile_id_core.types import ImageParams, OptionsParams

# Login to the Smile Identity portal to view your partner id.
partner_id: str = os.environ["PARTNER_ID"]
# Copy your API key from the Smile Identity portal.
api_key: str = os.environ["API_KEY"]
# '0':sandbox server, '1':production server.
sid_server: str = os.environ["SID_SERVER"]  # 0 or 1
default_callback = os.environ["DEFAULT_CALLBACK"]

connection = WebApi(partner_id, default_callback, api_key, sid_server)

# Create required tracking parameters
partner_params = {
    "job_id": f"job-{uuid.uuid4()}",  # Your unique job_id
    "user_id": f"user-{uuid.uuid4()}",  # Your unique user_id
    "job_type": JobType.SMART_SELFIE_REGISTRATION,
}


def create_base64_str(path: str) -> str:
    """Convert image to a base64 string.

    argument(s):
    path: path to the image file (string)

    Return: Returns a base64 string format of image file
    """
    with open(path, "rb") as binary_file:
        binary_file_data = binary_file.read()
        base64_data = base64.b64encode(binary_file_data)
        base64_img = base64_data.decode("utf-8")
        return base64_img


current_dir = os.path.dirname(os.path.abspath(__file__))
# selfie-file-path
selfie_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")
# base64image
base64image = create_base64_str(selfie_path)

"""Create image list.
 image_type_id Integer
 0 - Selfie image jpg or png (if you have the full path of the selfie)
 2 - Selfie image jpg or png base64 encoded (if you have the base64image
 string of the selfie)
 """

image_details: List[ImageParams] = [
    {
        "image_type_id": ImageTypes.SELFIE_IMAGE_STRING,  # 0 or 2
        "image": base64image,  # path to base64image string
    }
]

# Set the options for the job.
options = OptionsParams(
    # True: Gets job result in sync and result sent to callback
    # False: result is sent to callback url only
    return_job_status=True,  # True or False
    # True: Returns results of all jobs ran for the user plus current job
    # result. Set return_job_status to true to use this flag
    return_history=True,  # True or False
    # Set to true to receive selfie and liveness images you uploaded.
    # You must set return_job_status to true to use this flag.
    return_images=True,  # True or False
    use_enrolled_image=False,
)


def submit_job() -> None:
    """Submit job via the WebAPi."""
    result = connection.submit_job(
        partner_params,
        image_details,
        {},
        options,
    )
    print(result)


if __name__ == "__main__":
    submit_job()
