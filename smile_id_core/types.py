"""Define strict typings to paramters used throughout the SmileID SDK."""
import sys
from typing import Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

OptionsParams = TypedDict(
    "OptionsParams",
    {
        "return_job_status": bool,
        "return_history": bool,
        "return_images": bool,
        "use_enrolled_image": bool,
    },
)

SignatureParams = TypedDict(
    "SignatureParams",
    {
        "timestamp": str,
        "signature": str,
    },
)

Base64Image = TypedDict(
    "Base64Image",
    {
        "image_type_id": int,
        "image": str,
    },
)
FileImage = TypedDict(
    "FileImage",
    {
        "image_type_id": int,
        "file_name": str,
    },
)

ImageParams = Union[Base64Image, FileImage]
