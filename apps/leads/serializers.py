from rest_framework import serializers
from .models import Lead, Order


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ["id", "user", "product", "message", "status", "created_at"]
        read_only_fields = ["status", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "lead", "courier", "status", "created_at"]
