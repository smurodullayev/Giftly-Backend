from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import MediaFile


class MediaFileSerializer(serializers.ModelSerializer):
    """O'qish uchun — to'liq ma'lumotlar."""

    url = serializers.SerializerMethodField()
    size_kb = serializers.FloatField(read_only=True)
    uploaded_by_username = serializers.CharField(
        source="uploaded_by.username", read_only=True
    )

    class Meta:
        model = MediaFile
        fields = [
            "id", "url", "purpose",
            "original_filename", "mime_type",
            "size_bytes", "size_kb", "width", "height",
            "alt_text", "is_primary", "order",
            "uploaded_by", "uploaded_by_username",
            "created_at",
        ]
        read_only_fields = fields

    def get_url(self, obj) -> str:
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.url


class MediaUploadSerializer(serializers.Serializer):
    """
    Fayl yuklash uchun.

    Majburiy:
      file     — rasm fayl
      purpose  — MediaFile.Purpose tanlovlaridan biri

    Ixtiyoriy (bog'lash uchun):
      content_type_id — ContentType.pk (qaysi modelga bog'lash)
      object_id       — bog'lanadigan obyekt ID si

    Ixtiyoriy (ko'rsatish):
      alt_text    — SEO uchun alt matn
      is_primary  — asosiy rasm sifatida belgilash
      order       — tartib raqami
    """

    file = serializers.ImageField()
    purpose = serializers.ChoiceField(choices=MediaFile.Purpose.choices)
    content_type_id = serializers.IntegerField(required=False, allow_null=True)
    object_id = serializers.IntegerField(required=False, allow_null=True)
    alt_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_primary = serializers.BooleanField(required=False, default=False)
    order = serializers.IntegerField(required=False, default=0)

    def validate_file(self, value):
        # Kengaytma tekshiruvi
        ext = Path(value.name).suffix.lower()
        allowed = getattr(settings, "ALLOWED_IMAGE_EXTENSIONS", [".jpg", ".jpeg", ".png", ".webp", ".gif"])
        if ext not in allowed:
            raise serializers.ValidationError(
                f"Ruxsat etilgan kengaytmalar: {', '.join(allowed)}"
            )
        # Hajm tekshiruvi
        max_mb = getattr(settings, "MAX_UPLOAD_SIZE_MB", 10)
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"Fayl hajmi {max_mb} MB dan oshmasligi kerak."
            )
        return value

    def validate(self, attrs):
        ct_id = attrs.get("content_type_id")
        obj_id = attrs.get("object_id")
        # Ikkalasi yoki hech biri berilishi kerak
        if bool(ct_id) != bool(obj_id):
            raise serializers.ValidationError(
                "content_type_id va object_id birga berilishi yoki ikkalasi ham bo'sh bo'lishi kerak."
            )
        if ct_id:
            try:
                ContentType.objects.get(pk=ct_id)
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(
                    {"content_type_id": "Bunday ContentType mavjud emas."}
                )
        return attrs

    def create(self, validated_data):
        from PIL import Image as PilImage

        uploaded_file = validated_data["file"]
        ct_id = validated_data.pop("content_type_id", None)
        obj_id = validated_data.pop("object_id", None)

        # Rasm o'lchamlarini aniqlash
        width = height = None
        try:
            img = PilImage.open(uploaded_file)
            width, height = img.size
            uploaded_file.seek(0)
        except Exception:
            pass

        content_type = None
        if ct_id:
            content_type = ContentType.objects.get(pk=ct_id)

        media = MediaFile.objects.create(
            file=uploaded_file,
            purpose=validated_data["purpose"],
            original_filename=uploaded_file.name,
            mime_type=getattr(uploaded_file, "content_type", ""),
            size_bytes=uploaded_file.size,
            width=width,
            height=height,
            alt_text=validated_data.get("alt_text", ""),
            is_primary=validated_data.get("is_primary", False),
            order=validated_data.get("order", 0),
            content_type=content_type,
            object_id=obj_id,
            uploaded_by=self.context["request"].user,
        )
        return media


class MediaUpdateSerializer(serializers.ModelSerializer):
    """Faqat display parametrlarini yangilash (fayl o'zgarmaydi)."""

    class Meta:
        model = MediaFile
        fields = ["alt_text", "is_primary", "order"]
