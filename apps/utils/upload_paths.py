"""
Media fayl yo'llari — barcha upload_to callable funksiyalar shu yerda.

Konventsiya:  <purpose>/<uuid>.<ext>

Keyinchalik S3 / Cloudinary ga o'tganda faqat
DEFAULT_FILE_STORAGE (yoki STORAGES) sozlamasini o'zgartirish yetarli —
fayl yo'llari o'zgarmaydi.
"""
import uuid
from pathlib import Path


def _make_path(prefix: str, filename: str) -> str:
    """UUID asosida noyob fayl nomi yaratadi, kengaytmani saqlaydi."""
    ext = Path(filename).suffix.lower()
    return f"{prefix}/{uuid.uuid4()}{ext}"


def media_file_upload(instance, filename: str) -> str:
    """
    MediaFile modeli uchun umumiy upload_to.
    Fayl manzili: media/<purpose>/<uuid>.<ext>
    """
    purpose = getattr(instance, "purpose", "other") or "other"
    return _make_path(f"media/{purpose}", filename)
