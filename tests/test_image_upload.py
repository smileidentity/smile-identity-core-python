import io
import os
import tempfile
import zipfile

import pytest

from smile_id_core.image_upload import (
    prepare_image_entry_dict,
    prepare_info_json,
    generate_zip_file,
    prepare_image_payload,
    validate_images,
)


def test_prepare_image_entry_dict():
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


def test_prepare_info_json():
    image_params = [
        {
            "image": "directory/file.jpg",
            "image_type_id": 5,
        }
    ]

    info_json = prepare_info_json(
        partner_id="partner_id",
        callback_url="callback_url",
        upload_url="upload_url",
        partner_params="partner_params",
        image_params=image_params,
        id_info_params="id_info_params",
        sec_params={
            "sec_key": "sec_key",
            "timestamp": "timestamp",
        },
    )
    assert info_json["id_info"] == "id_info_params"
    assert info_json["images"] == prepare_image_payload(image_params)
    assert info_json["misc_information"]["smile_client_id"] == "partner_id"


@pytest.fixture()
def temp_image_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
        temp_image_file.write(b"test image data")

    yield temp_image_file.name

    os.remove(temp_image_file.name)


def test_generate_zip_file(temp_image_file):

    assert temp_image_file.endswith(".jpg")

    image_params = [
        {
            "image": temp_image_file,
            "image_type_id": 5,
        }
    ]

    zip_stream = generate_zip_file(
        partner_id="partner_id",
        callback_url="callback_url",
        upload_url="upload_url",
        partner_params="partner_params",
        image_params=image_params,
        id_info_params="id_info_params",
        sec_params={"sec_key": "sec_key", "timestamp": "timestamp"},
    )

    zf = zipfile.ZipFile(io.BytesIO(zip_stream))
    assert zf.namelist() == ["info.json", os.path.basename(temp_image_file)]


def test_validate_images__ok_file_exists(temp_image_file):
    image_params = [
        {
            "image": temp_image_file,
            "image_type_id": 0,
        }
    ]

    assert validate_images(image_params) is None


def test_validate_images__error_file_not_found():
    image_params = [
        {
            "image": "nonexistent/file.jpg",
            "image_type_id": 5,
        }
    ]

    with pytest.raises(FileNotFoundError):
        validate_images(image_params)


def test_validate_images_jt6_id_not_provided():
    image_params = [
        {
            "image": "wwsss===",
            "image_type_id": 5,
        }
    ]

    with pytest.raises(ValueError):
        validate_images(image_params, 6)
