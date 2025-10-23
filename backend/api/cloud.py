import os
from typing import Tuple, Optional

from django.conf import settings

# optional import
try:
    import cloudinary
    import cloudinary.uploader
except Exception:
    cloudinary = None


def init_cloudinary():
    if settings.USE_CLOUDINARY and cloudinary is not None:
        cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL, secure=True)


def upload_image(file_path: str, public_id: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Returns (ok, url, error)
    """
    if not settings.USE_CLOUDINARY or cloudinary is None:
        return False, None, "Cloudinary not configured"
    try:
        init_cloudinary()
        res = cloudinary.uploader.upload(file_path, public_id=public_id)
        return True, res.get("secure_url") or res.get("url"), None
    except Exception as e:
        return False, None, str(e)