"""Prepare & validate image data, and generate zipped file to be submitted."""
import io
import json
import os
import zipfile
from typing import Any, ByteString, Dict, List, Optional, cast

from smile_id_core import constants
from smile_id_core.constants import JobType
from smile_id_core.types import (
    Base64Image,
    FileImage,
    ImageParams,
    SignatureParams,
)
from smile_id_core.Utilities import validate_signature_params


class ApiVersion:
    """Specify API version details."""

    BUILD_NUMBER = 0
    MAJOR_VERSION = 2
    MINOR_VERSION = 0


IMAGE_FILE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def generate_zip_file(
    partner_id: str,
    callback_url: str,
    upload_url: str,
    partner_params: Dict[str, Any],
    image_params: List[ImageParams],
    id_info_params: Dict[str, str],
    signature_params: SignatureParams,
) -> ByteString:
    """Create zipped file with a number of various params.

    argument(s):
        partner_id
        callback_url
        upload_url
        partner_params
        image_params
        id_info_params
        signature params
    Returns: zipped filed of ByteString type
    """
    info_json = prepare_info_json(
        partner_id,
        callback_url,
        upload_url,
        partner_params,
        image_params,
        id_info_params,
        signature_params,
    )
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        zip_buffer, "a", zipfile.ZIP_DEFLATED, False
    ) as zip_file:
        zip_file.writestr("info.json", data=json.dumps(info_json))
        for image in image_params:
            if (
                "image" in image
                and image["image_type_id"] in constants.BASE64_IMAGE_TYPES
            ):
                image = cast(Base64Image, image)
                zip_file.writestr(
                    "base64imgString", os.path.basename(image["image"])
                )
            elif (
                "file_name" in image
                and image["image_type_id"] in constants.FILENAME_IMAGE_TYPES
            ):
                image = cast(FileImage, image)
                if image["file_name"] is not None:
                    zip_file.write(
                        image["file_name"],
                        os.path.basename(image["file_name"]),
                    )
    return zip_buffer.getvalue()


def prepare_info_json(
    partner_id: str,
    callback_url: str,
    upload_url: str,
    partner_params: Dict[str, str],
    image_params: List[ImageParams],
    id_info_params: Dict[str, str],
    signature_params: SignatureParams,
) -> Dict[str, Any]:
    """Call validate_signature_params to validate signature params.

    argument(s):
    partner_id
    callback_url
    upload_url
    partner_params,
    image_params
    id_info_params
    signature params
    Returns: Dict response
    """
    validate_signature_params(signature_params)
    return {
        "package_information": {
            "apiVersion": {
                "buildNumber": ApiVersion.BUILD_NUMBER,
                "majorVersion": ApiVersion.MAJOR_VERSION,
                "minorVersion": ApiVersion.MINOR_VERSION,
            },
            "language": "python",
        },
        "misc_information": {
            **signature_params,
            "retry": "false",
            "partner_params": partner_params,
            "file_name": "selfie.zip",
            "smile_client_id": partner_id,
            "callback_url": callback_url,
            "userData": {
                "isVerifiedProcess": False,
                "name": "",
                "fbUserID": "",
                "firstName": "",
                "lastName": "",
                "gender": "",
                "email": "",
                "phone": "",
                "countryCode": "+",
                "countryName": "",
            },
        },
        "id_info": id_info_params,
        "images": prepare_image_payload(image_params),
        "server_information": upload_url,
    }


def prepare_image_payload(
    image_params: List[ImageParams],
) -> List[Dict[str, Any]]:
    """Call the prepare_image_entry_dict on image params.

    argument(s):
        image_params: images details of type Dict of List. Contains image type
        id, a path or base64 string to the image(id doc or selfie).
    Returns: Dict of list return based on image format(base64 or image file)
    """
    image_lists = []
    for image in image_params:
        type_id = int(image["image_type_id"])
        file = ""

        if "image" in image.keys() and image.get("image") is not None:
            file = str(image.get("image"))
        if "file_name" in image.keys():
            file = str(image.get("file_name"))
        image_lists.append(prepare_image_entry_dict(file, type_id))
    return image_lists


def prepare_image_entry_dict(
    image: Optional[str], image_type_id: int
) -> Dict[str, Any]:
    """Check for image format and return image info as dict.

    argument(s):
        image: Image is a dictionary of a list and it contains image data info
        .The value to the key could be a string specifying path to an image
        file or a base64 image string.
        image_type_id: This is an int value which specifies which kind of
        image data is provided based on it's unique value.

    Returns:
    Returns an image data dictionary containing image_type_id, image, the
    filename.
    """
    if image and image.lower().endswith(IMAGE_FILE_EXTENSIONS):
        return {
            "image_type_id": image_type_id,
            "image": "",
            "file_name": os.path.basename(image),
        }
    return {
        "image_type_id": image_type_id,
        "image": image,
        "file_name": "",
    }


def validate_images(
    images_params: List[ImageParams],
    use_enrolled_image: bool = False,
    job_type: Optional[JobType] = None,
) -> bool:
    """Perform validation checks on images_params.

    argument(s):
        image_params of type List
        use_enrolled_imge: bool
        job_type: specifies job type

    Returns: A boolean value based on checks for jobtype 6
    """
    if not images_params:
        raise ValueError("Please ensure that you send through image details")

    if not isinstance(images_params, list):
        raise ValueError(
            "Please ensure that you send through image details as a list"
        )

    has_id_image = False
    has_selfie = False
    for image in images_params:
        image_file_name = image.get("file_name", None)
        base64_image = image.get("image", None)
        image_type = image.get("image_type_id", None)

        if image_type is None:
            raise ValueError("image_type_id cannot be None or empty")
        if base64_image and image_file_name:
            raise ValueError("image and file_name both can't exist")
        if not base64_image and not image_file_name:
            raise ValueError("image or file_name keys both can't be empty")
        if base64_image and image_type in constants.FILENAME_IMAGE_TYPES:
            raise ValueError("check for image_type_id and image file mismatch")
        if image_file_name and image_type in constants.BASE64_IMAGE_TYPES:
            raise ValueError(
                "check for image_type_id and base64 image mismatch"
            )
        if image_file_name and isinstance(image_file_name, str):
            if image_file_name.lower().endswith(
                IMAGE_FILE_EXTENSIONS
            ) and not os.path.exists(image_file_name):
                raise FileNotFoundError(
                    f"No such file or directory {image_file_name}"
                )

        image_type_id = image["image_type_id"]
        if image_type_id == 1 or image_type_id == 3:
            has_id_image = True
        if image_type_id == 0 or image_type_id == 2:
            has_selfie = True

    is_docv_job = (
        job_type == JobType.DOCUMENT_VERIFICATION
        or job_type == JobType.ENHANCED_DOCUMENT_VERIFICATION
    )
    if is_docv_job and not has_id_image:
        raise ValueError(
            "You are attempting to complete a Document Verification job "
            "without providing an id card image."
        )

    if not (has_selfie or (is_docv_job and use_enrolled_image)):
        raise ValueError("You need to send through at least one selfie image.")

    if (
        has_id_image
        and has_selfie
        and (is_docv_job and use_enrolled_image)
        and (is_docv_job and not has_id_image)
    ):
        return False
    return True
