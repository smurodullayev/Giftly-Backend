from rest_framework import serializers
from .models import User, BusinessProfile, CourierProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone"]


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ["id", "user", "company_name", "description", "subscription_plan"]


class CourierProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        fields = ["id", "user", "vehicle_type", "is_available"]
