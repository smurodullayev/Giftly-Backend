"""
apps/media — barcha media fayllar uchun markazlashgan app.

GenericForeignKey pattern: MediaFile ixtiyoriy modelga bog'lanadi.
Yangi model uchun media kerak bo'lsa — bu faylga teginmasdan bo'ladi.

  User avatari:        purpose='user_avatar',   content_object=user_instance
  Biznes logotipi:     purpose='business_logo', content_object=business_profile
  Mahsulot rasmi:      purpose='product_image', content_object=product
  Kelajakda boshqa:    purpose='other',         content_object=<any>
"""
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.utils.upload_paths import media_file_upload


class MediaFile(models.Model):
    class Purpose(models.TextChoices):
        USER_AVATAR = "user_avatar", "Foydalanuvchi avatari"
        BUSINESS_LOGO = "business_logo", "Biznes logotipi"
        PRODUCT_IMAGE = "product_image", "Mahsulot rasmi"
        OTHER = "other", "Boshqa"

    # ------------------------------------------------------------------
    # Fayl
    # ------------------------------------------------------------------
    file = models.ImageField(
        upload_to=media_file_upload,
        verbose_name="Fayl",
    )
    purpose = models.CharField(
        max_length=50,
        choices=Purpose.choices,
        default=Purpose.OTHER,
        db_index=True,
        verbose_name="Maqsad",
    )

    # ------------------------------------------------------------------
    # Metadata — yuklash paytida to'ldiriladi
    # ------------------------------------------------------------------
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Asl fayl nomi",
    )
    mime_type = models.CharField(max_length=100, blank=True, verbose_name="MIME turi")
    size_bytes = models.PositiveIntegerField(default=0, verbose_name="Hajm (bayt)")
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kenglik (px)")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="Balandlik (px)")

    # ------------------------------------------------------------------
    # Ko'rsatish parametrlari
    # ------------------------------------------------------------------
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Alt matn",
        help_text="SEO va accessibility uchun",
    )
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Asosiy",
        help_text="User avatari yoki mahsulotning bosh rasmi",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tartib",
        help_text="Kichik raqam — oldinroq ko'rsatiladi",
    )

    # ------------------------------------------------------------------
    # GenericForeignKey — ixtiyoriy modelga bog'lash
    # ------------------------------------------------------------------
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Bog'liq model turi",
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Bog'liq obyekt ID",
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # ------------------------------------------------------------------
    # Kim yukladi
    # ------------------------------------------------------------------
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
        verbose_name="Yuklagan",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Media fayl"
        verbose_name_plural = "Media fayllar"
        ordering = ["order", "-is_primary", "created_at"]
        indexes = [
            # Bitta obyektning barcha media fayllarini tez olish uchun
            models.Index(
                fields=["content_type", "object_id"],
                name="media_ct_obj_idx",
            ),
            # Purpose + obyekt kombinatsiyasi (masalan: mahsulotning barcha rasmlari)
            models.Index(
                fields=["purpose", "content_type", "object_id"],
                name="media_purpose_ct_obj_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.get_purpose_display()}] {self.original_filename or self.pk}"

    def save(self, *args, **kwargs):
        # Agar is_primary=True bo'lsa, xuddi shu obyektning boshqasini False qilish
        if self.is_primary and self.content_type and self.object_id:
            MediaFile.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    @property
    def url(self) -> str:
        return self.file.url if self.file else ""

    @property
    def size_kb(self) -> float:
        return round(self.size_bytes / 1024, 1)
