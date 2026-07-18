from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "Foydalanuvchi"
        BUSINESS = "business", "Biznes"
        COURIER = "courier", "Kuryer"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_business(self) -> bool:
        return self.role == self.Role.BUSINESS

    @property
    def is_courier(self) -> bool:
        return self.role == self.Role.COURIER


class BusinessProfile(models.Model):
    class SubscriptionPlan(models.TextChoices):
        FREE = "free", "Bepul"
        BASIC = "basic", "Asosiy"
        PRO = "pro", "Pro"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="business_profile",
        limit_choices_to={"role": User.Role.BUSINESS},
    )
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Biznes profili"
        verbose_name_plural = "Biznes profillari"

    def __str__(self) -> str:
        return self.company_name


class CourierProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="courier_profile",
        limit_choices_to={"role": User.Role.COURIER},
    )
    vehicle_type = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kuryer profili"
        verbose_name_plural = "Kuryer profillari"

    def __str__(self) -> str:
        return f"Kuryer: {self.user.username}"
