"""Unit tests for different constants used across the SmileAPI"""
from smile_id_core.constants import ImageTypes, JobType

def test_image_types() -> None:
    """Tests that image type values match the proper numeric tags"""
    assert ImageTypes.SELFIE_FILE.value == 0
    assert ImageTypes.ID_CARD_FILE.value == 1
    assert ImageTypes.SELFIE_IMAGE_STRING.value == 2
    assert ImageTypes.ID_CARD_IMAGE_STRING.value == 3
    assert ImageTypes.LIVENESS_IMAGE_FILE.value == 4
    assert ImageTypes.ID_CARD_BACK_FILE.value == 5
    assert ImageTypes.LIVENESS_IMAGE_STRING.value == 6
    assert ImageTypes.ID_CARD_BACK_STRING.value == 7

def test_job_types() -> None:
    """Tests that job type values match the proper numeric tags"""
    assert JobType.BIOMETRIC_KYC.value == 1
    assert JobType.SMART_SELFIE_AUTHENTICATION.value == 2
    assert JobType.SMART_SELFIE_REGISTRATION.value == 4
    assert JobType.BASIC_KYC.value == 5
    assert JobType.ENHANCED_KYC.value == 5
    assert JobType.DOCUMENT_VERIFICATION.value == 6
    assert JobType.BUSINESS_VERIFICATION.value == 7
    assert JobType.UPDATE_PHOTO.value == 8
    assert JobType.COMPARE_USER_INFO.value == 9
