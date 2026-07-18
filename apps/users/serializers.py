from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import BusinessProfile, CourierProfile, User


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """O'qish uchun — parol ko'rsatilmaydi."""

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "phone", "date_joined", "updated_at",
        ]
        read_only_fields = ["id", "date_joined", "updated_at"]


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
            "role", "phone", "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Parollar mos kelmadi."}
            )
        role = attrs.get("role", User.Role.USER)
        if role == User.Role.ADMIN:
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
        user = self.context["request"].user
        if not user.check_password(value):
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
    class Meta:
        model = BusinessProfile
        fields = [
            "id", "user", "company_name", "description",
            "subscription_plan", "updated_at",
        ]
        read_only_fields = ["id", "user", "updated_at"]

    def validate_user(self, value):
        if value.role != User.Role.BUSINESS:
            raise serializers.ValidationError(
                "Faqat 'business' rolidagi foydalanuvchi profil yarata oladi."
            )
        return value

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
