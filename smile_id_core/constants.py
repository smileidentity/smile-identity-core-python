"""Contains constants used across smile, like image types and job types."""
import typing
from enum import IntEnum


class ImageTypes(IntEnum):
    """Represents the different ImageType codes used by the SmileAPI."""

    SELFIE_FILE = 0  # Selfie image in a file format
    ID_CARD_FILE = 1  # ID card image in a file format
    SELFIE_IMAGE_STRING = 2  # Selfie image as a base64 image string
    ID_CARD_IMAGE_STRING = 3  # ID card as a base64 image string
    LIVENESS_IMAGE_FILE = 4  # Liveness image in a file format
    ID_CARD_BACK_FILE = 5  # ID card image(back) in a file format
    LIVENESS_IMAGE_STRING = 6  # Liveness image as a base64 image string
    ID_CARD_BACK_STRING = 7  # ID card image(back)as a base64 image string


class JobType(IntEnum):
    """Represents the different JobType codes used by the SmileAPI."""

    # Verifies the ID information of your users using facial biometrics
    BIOMETRIC_KYC = 1

    # Compares a selfie to a selfie on file.
    SMART_SELFIE_AUTHENTICATION = 2

    # Creates an enrollee, associates a selfie with a partner_id, user_id
    SMART_SELFIE_REGISTRATION = 4

    # Queries Identity Information of user using ID_number.
    ENHANCED_KYC = 5

    # Verifies identity information of a person with their personal
    # information and ID number from one of our supported ID Types.
    BASIC_KYC = 5

    # Verifies user info retrieved from the ID issuing authority.
    DOCUMENT_VERIFICATION = 6

    # Verifies authenticity of Document IDs, confirms it's linked to the user
    # using facial biometrics.
    BUSINESS_VERIFICATION = 7

    # Updates the photo on file for an enrolled user
    UPDATE_PHOTO = 8

    # Compares document verification to an id check
    COMPARE_USER_INFO = 9

    # Verifies user selfie with info retrieved from the ID issuing authority.
    ENHANCED_DOCUMENT_VERIFICATION = 11


# Defines production and sandbox test endpoints

sid_server_map = {
    0: "https://testapi.smileidentity.com/v1",
    1: "https://api.smileidentity.com/v1",
}

# See https://docs.usesmileid.com/further-reading/faqs/what-are-the-image-types-i-can-upload-to-smile-id
FILENAME_IMAGE_TYPES: typing.List[int] = [0, 1, 4, 5]
BASE64_IMAGE_TYPES: typing.List[int] = [2, 3, 6, 7]
