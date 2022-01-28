import json
import zipfile
import io
import os
from smile_id_core.Utilities import validate_sec_params


class ApiVersion:
    BUILD_NUMBER = 0
    MAJOR_VERSION = 2
    MINOR_VERSION = 0


IMAGE_FILE_EXTENSIONS = (".png", ".jpg")


def generate_zip_file(
    partner_id,
    callback_url,
    upload_url,
    partner_params,
    image_params,
    id_info_params,
    sec_params,
):
    info_json = prepare_info_json(
        partner_id,
        callback_url,
        upload_url,
        partner_params,
        image_params,
        id_info_params,
        sec_params,
    )
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("info.json", data=json.dumps(info_json))
        for image in image_params:
            image_file_path = image["image"]
            if isinstance(image_file_path, str) and image_file_path.lower().endswith(
                IMAGE_FILE_EXTENSIONS
            ):
                # TODO: do we really silently skip a file if its extension is different?
                zip_file.write(image_file_path, os.path.basename(image_file_path))
    return zip_buffer.getvalue()


def prepare_info_json(
    partner_id,
    callback_url,
    upload_url,
    partner_params,
    image_params,
    id_info_params,
    sec_params,
):
    validate_sec_params(sec_params)
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
            **sec_params,
            "retry": "false",
            "partner_params": partner_params,
            "file_name": "selfie.zip",
            "smile_client_id": partner_id,
            "callback_url": callback_url,
            "userData": {
                "isVerifiedProcess": False,
                "name": "",
                "fbUserID": "",
                "firstName": "Bill",
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


def prepare_image_payload(image_params):
    return [prepare_image_entry_dict(**image) for image in image_params]


def prepare_image_entry_dict(image, image_type_id, **_):
    if isinstance(image, bytes):
        image = image.decode("utf-8")
    elif image.lower().endswith(IMAGE_FILE_EXTENSIONS):
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


def validate_images(images_params, use_enrolled_image=False, job_type=None):
    if not images_params:
        raise ValueError("Please ensure that you send through image details")

    if not isinstance(images_params, list):
        raise ValueError("Please ensure that you send through image details as a list")

    for image in images_params:
        if isinstance(image["image"], str) and image["image"].lower().endswith(
            IMAGE_FILE_EXTENSIONS
        ):
            if not os.path.exists(image["image"]):
                raise FileNotFoundError(
                    "No such file or directory %s" % (image["image"])
                )

    if len(images_params) == 0 or not (
        has_selfie_image(images_params) or (job_type == 6 and use_enrolled_image)
    ):
        raise ValueError("You need to send through at least one selfie image")


def has_selfie_image(images_params):
    found = False
    for image in images_params:
        image_type_id = int(image["image_type_id"])
        if image_type_id == 0 or image_type_id == 2:
            found = True
            break
    return found
