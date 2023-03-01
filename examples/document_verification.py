"""Document Verification class; verifies authentitcity of docs.

This product lets you verify the authenticity of ID documents submitted by
users and confirm these document actually belongs to the user by comparing the
user's selfie to the photo on the document.

Requirements to run this job:
1. A selfie of the user
2. An image of the document
3. Document type
4. Country of issuance.
See
https://docs.smileidentity.com/products/for-individuals-kyc/document-verification
for how to setup and retrieve configuration values for the WebApi class.
"""

import base64
import os
import uuid
from typing import List

from smile_id_core import WebApi
from smile_id_core.types import ImageParams, OptionsParams

# Login to the Smile Identity portal to view your partner id.
partner_id: str = os.environ["PARTNER_ID"]
# Copy your API key from the Smile Identity portal.
api_key: str = os.environ["API_KEY"]
# '0':sandbox server, '1':production server.
sid_server: str = os.environ["SID_SERVER"]  # 0 or 1
default_callback = os.environ["DEFAULT_CALLBACK"]

connection = WebApi(partner_id, default_callback, api_key, sid_server)

# Create required tracking parameters.
partner_params = {
    "job_id": f"job-{uuid.uuid4()}",  # your unique job_id
    "user_id": f"user-{uuid.uuid4()}",  # your unique user_id
    "job_type": 6,
}


def create_base64_str(path: str) -> str:
    """Convert image to a base64 string.

    argument(s):
    path: path to the image file

    Return:
    Returns a base64 string format of image file
    """
    with open(path, "rb") as binary_file:
        base64_data = base64.b64encode(binary_file.read())
        base64_img = base64_data.decode("utf-8")
        return base64_img


current_dir = os.path.dirname(os.path.abspath(__file__))

# selfie-file-path
image_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")
# selfie-base64-string
base64image = create_base64_str(image_path)


"""Create image list.

  image_type_id Integer
  0 - Selfie image in .png or .jpg file format
  1 - ID card image in .png or .jpg file format
  2 - Base64 encoded selfie image in .png or .jpg file format
  3 - Base64 encoded ID card image in .png or .jpg file format
  4 - Liveness image in .png or .jpg file format file format (if you have the
  full path of the liveness image).
  5 - Back of ID card image in .png or .jpg file format
  6 - Base64 encoded liveness image in .jpg or .png file format (if you have
  the base64image string of the liveness image)
  7 - Base64 encoded back of ID card image .jpg or .png file format (if you
  have the full path of the selfie)

You may use the recommended web sdk to capture the images
"""
image_details: List[ImageParams] = [
    {
        "image_type_id": 0,  # 0 or 2
        "file_name": image_path,  # path to selfie image or base64image string
    },
    {
        # Not required if you don't require proof of life (note photo of photo
        # check will still be performed on the uploaded selfie)
        "image_type_id": 6,  # 4 or 6
        "image": base64image,  # path to liveness base64image string
    },
    {
        "image_type_id": 1,  # 1 or 3
        "file_name": image_path,  # path to front of id document image string
    },
    {
        # Optional, only use if you're uploading the back of the id document
        # image
        "image_type_id": 7,  # 5 or 7
        "image": base64image,  # path to back of id document base64image string
    },
]

# The ID Document Information
id_info = {
    "country": "NG",  # ID document country of issue 2-letter country code
    "id_type": "PASSPORT",
}

# Set the options for the job.
options = OptionsParams(
    # True: Gets job result in sync and result sent to callback
    # False: result is sent to callback url only
    return_job_status=True,
    # True: Returns results of all jobs ran for the user plus current job
    # result. Set return_job_status to true to use this flag
    return_history=True,
    # Set to true to receive selfie and liveness images you uploaded.
    # You must set return_job_status to true to use this flag.
    return_images=True,
    use_enrolled_image=False,
)


def submit_job() -> None:
    """Submit job via the WebAPi."""
    result = connection.submit_job(
        partner_params, image_details, id_info, options
    )
    print(result)


if __name__ == "__main__":
    submit_job()
