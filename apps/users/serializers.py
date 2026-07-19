from typing import Optional

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import BusinessProfile, CourierProfile, User


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """O'qish uchun — parol va maxfiy ma'lumotlar ko'rsatilmaydi."""

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "phone", "birth_date", "address", "telegram",
            "bio", "is_verified", "avatar_url",
            "date_joined", "updated_at",
        ]
        read_only_fields = ["id", "is_verified", "date_joined", "updated_at", "avatar_url"]

    def get_avatar_url(self, obj) -> Optional[str]:
        """Foydalanuvchining asosiy avatarini MediaFile dan olish."""
        from django.contrib.contenttypes.models import ContentType
        from apps.media.models import MediaFile
        ct = ContentType.objects.get_for_model(obj)
        media = (
            MediaFile.objects
            .filter(content_type=ct, object_id=obj.pk, purpose="user_avatar")
            .order_by("-is_primary", "order")
            .first()
        )
        if not media:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(media.file.url) if request else media.file.url


class RegisterSerializer(serializers.ModelSerializer):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name",
            "role", "phone", "birth_date", "address", "telegram",
            "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Parollar mos kelmadi."}
            )
        if attrs.get("role") == User.Role.ADMIN:
            raise serializers.ValidationError(
                {"role": "Admin rolini ro'yxatdan o'tish orqali olish mumkin emas."}
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user


# ---------------------------------------------------------------------------
# BusinessProfile
# ---------------------------------------------------------------------------

class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Biznes profili — logo va logotip to'g'ridan-to'g'ri ImageField orqali.

    Rasm yuklash uchun so'rov multipart/form-data bo'lishi shart:
      logo     → ikonka/belgi rasmi (PNG, kvadrat)
      logotype → matnli to'liq logo (PNG/JPG, keng formatda)

    logo_url / logotype_url — faqat o'qish uchun (GET javobida keladi).
    """

    logo_url = serializers.SerializerMethodField()
    logotype_url = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfile
        fields = [
            "id", "user",
            "company_name", "description",
            "phone", "address", "website", "instagram_url", "telegram_username",
            # Rasmlar: yuklanadigan field + o'qiladigan URL
            "logo", "logo_url",
            "logotype", "logotype_url",
            "subscription_plan", "is_verified",
            "updated_at",
        ]
        read_only_fields = [
            "id", "user", "is_verified",
            "logo_url", "logotype_url",
            "updated_at",
        ]
        extra_kwargs = {
            # logo va logotype write-only emas, lekin javobda URL ko'rinadi
            "logo": {"write_only": True, "required": False},
            "logotype": {"write_only": True, "required": False},
        }

    def get_logo_url(self, obj) -> Optional[str]:
        if not obj.logo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

    def get_logotype_url(self, obj) -> Optional[str]:
        if not obj.logotype:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.logotype.url) if request else obj.logotype.url

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


# ---------------------------------------------------------------------------
# CourierProfile
# ---------------------------------------------------------------------------

class CourierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        fields = ["id", "user", "vehicle_type", "is_available", "updated_at"]
        read_only_fields = ["id", "user", "updated_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
