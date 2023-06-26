import base64
import io
import os
import tempfile
import zipfile
from typing import List

import pytest

from smile_id_core.constants import JobType
from smile_id_core.image_upload import (
    generate_zip_file,
    prepare_image_entry_dict,
    prepare_image_payload,
    prepare_info_json,
    validate_images,
)
from smile_id_core.types import ImageParams

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "../tests/fixtures/1pixel.jpg")

with open(image_path, "rb") as binary_file:
    base64_data = base64.b64encode(binary_file.read())
    base64_img = base64_data.decode("utf-8")

def test_prepare_image_entry_dict():
    """Tests image entry dict"""
    assert prepare_image_entry_dict("directory/file.jpg", 5) == {
        "image_type_id": 5,
        "image": "",
        "file_name": "file.jpg",
    }
    assert prepare_image_entry_dict("directory/file.txt", 5) == {
        "image_type_id": 5,
        "image": "directory/file.txt",
        "file_name": "",
    }

    with open(image_path, "rb") as image:
        encoded_string = base64.b64encode(image.read())
        image_file_path = base64.b64decode(encoded_string).decode("utf-8")

    assert prepare_image_entry_dict(image_file_path, 5) == {
        "image_type_id": 5,
        "image": image_file_path,
        "file_name": "",
    }

    assert (
        prepare_image_entry_dict(image_file_path, 5)["image"] == image_file_path
    )

def test_prepare_info_json():
    """Validates inputs to prepare_info_json function"""
    image_params: List[ImageParams] = [
        {
            "image_type_id": 5,
            "file_name": "directory/file.jpg",
        }
    ]

    info_json = prepare_info_json(
        partner_id="partner_id",
        callback_url="callback_url",
        upload_url="upload_url",
        partner_params="partner_params",  # type: ignore
        image_params=image_params,
        id_info_params="id_info_params",  # type: ignore
        signature_params={
            "signature": "signature",
            "timestamp": "timestamp",
        },
    )
    assert info_json["id_info"] == "id_info_params"
    assert info_json["images"] == prepare_image_payload(image_params)
    assert info_json["misc_information"]["smile_client_id"] == "partner_id"

@pytest.fixture()
def temp_image_file():
    """Creates temp image file (Generator)"""
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".jpg"
    ) as temp_image_file:
        temp_image_file.write(b"test image data")

    yield temp_image_file.name

    os.remove(temp_image_file.name)

def test_generate_zip_file() -> None:
    """Generates zipped file with temp_image_file"""
    assert image_path.endswith(".jpg")

    image_params: List[ImageParams] = [
        {
            "image_type_id": 5,
            "file_name": image_path,
        }
    ]

    zip_stream = generate_zip_file(
        partner_id="partner_id",
        callback_url="callback_url",
        upload_url="upload_url",
        partner_params="partner_params",  # type: ignore
        image_params=image_params,
        id_info_params="id_info_params",  # type: ignore
        signature_params={"signature": "signature", "timestamp": "timestamp"},
    )

    with zipfile.ZipFile(io.BytesIO(bytes(zip_stream))) as zipped_file:
        assert zipped_file.namelist() == [
            "info.json",
            os.path.basename(image_path),
        ]

def test_validate_images__ok_file_exists() -> None:
    """Validates image file exists (is Not None)"""
    image_params: List[ImageParams] = [
        {
            "image_type_id": 0,
            "file_name": image_path,
        }
    ]

    assert validate_images(image_params) is not None

def test_validate_images__error_file_not_found():
    """Validates that non-existent image files is not found"""
    image_params: List[ImageParams] = [
        {
            "image_type_id": 5,
            "file_name": "nonexistent/file.jpg",
        }
    ]

    with pytest.raises(FileNotFoundError) as exc_info:
        validate_images(image_params)
    assert (
        str(exc_info.value) == "No such file or directory nonexistent/file.jpg"
    )

def test_validate_images_jt6_id_not_provided() -> None:
    """Tests for missing id card for document verification"""
    image_params: List[ImageParams] = [
        {
            "image_type_id": 0,
            "file_name": image_path,
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(image_params, job_type=JobType.DOCUMENT_VERIFICATION)
    assert (
        str(exc_info.value)
        == "You are attempting to complete a Document Verification job without"
        " providing an id card image."
    )

def test_validate_images_require_a_selfie_for_alljt_except_jt6() -> None:
    """Checks that image validation for all job types other than
    document verification have at least 1 selfie image"""
    image_params: List[ImageParams] = [
        {
            "image_type_id": 1,
            "file_name": image_path,
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.BIOMETRIC_KYC,
            use_enrolled_image=False,
        )
    assert (
        str(exc_info.value)
        == "You need to send through at least one selfie image."
    )

def test_validate_images_require_a_selfie_when_enrolled_image_is_false_jt6() -> (
    None
):
    """Checks that attempted image validation for all job types other than
    document verification require at least 1 selfie image with
    use_enrolled_image set to false"""

    image_params: List[ImageParams] = [
        {
            "image_type_id": 1,
            "file_name": image_path,
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=False,
        )
    assert (
        str(exc_info.value)
        == "You need to send through at least one selfie image."
    )

def test_validate_images_require_no_selfie_when_enrolled_image_is_true_jt6() -> (
    None
):
    image_params: List[ImageParams] = [
        {
            "image_type_id": 1,
            "file_name": image_path,
        }
    ]

    assert (
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=True,
        )
        is True
    )

def test_validate_images_params():
    image_params: List[ImageParams] = [
        {
            "image_type_id": 5,
            "file_name": "",
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=True,
        )
    assert str(exc_info.value) == "image or file_name keys both can't be empty"

    image_params = [
        {
            "image": base64_img,
            "image_type_id": 5,
            "file_name": image_path,
        }  # type: ignore
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=True,
        )
    assert str(exc_info.value) == "image and file_name both can't exist"

    image_params = [
        {
            "image_type_id": 3,
            "file_name": image_path,
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=True,
        )
    assert (
        str(exc_info.value)
        == "check for image_type_id and base64 image mismatch"
    )

    image_params = [
        {
            "image": base64_img,
            "image_type_id": 1,
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.DOCUMENT_VERIFICATION,
            use_enrolled_image=True,
        )
    assert (
        str(exc_info.value) == "check for image_type_id and image file mismatch"
    )

    image_params: List[ImageParams] = [{"image": base64_img, "image_type_id": None}]  # type: ignore

    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,
            job_type=JobType.BIOMETRIC_KYC,
            use_enrolled_image=True,
        )
    assert str(exc_info.value) == "image_type_id cannot be None or empty"

def test_validate_image_is_a_list():
    image_params = {"image": base64_img, "image_type_id": 4}
    with pytest.raises(ValueError) as exc_info:
        validate_images(
            image_params,  # type: ignore
            job_type=JobType.BIOMETRIC_KYC,
            use_enrolled_image=True,
        )
    assert (
        str(exc_info.value)
        == "Please ensure that you send through image details as a list"
    )
