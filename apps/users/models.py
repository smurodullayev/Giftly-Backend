from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        BUSINESS = "business", "Business"
        COURIER = "courier", "Kuryer"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subscription_plan = models.CharField(max_length=50, default="free")

    def __str__(self):
        return self.company_name


class CourierProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="courier_profile")
    vehicle_type = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Kuryer: {self.user.username}"
