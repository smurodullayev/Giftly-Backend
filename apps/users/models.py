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
        verbose_name="Rol",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name="Telefon",
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tug'ilgan sana",
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Manzil",
    )
    telegram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Telegram",
        help_text="@ belgisisiz, masalan: username",
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Qisqacha ma'lumot",
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tasdiqlangan",
        help_text="Telefon yoki email orqali tasdiqlangan hisob",
    )
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
    company_name = models.CharField(max_length=255, verbose_name="Kompaniya nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Biznes telefon",
        help_text="Kompaniya bog'lanish raqami",
    )
    address = models.CharField(max_length=500, blank=True, verbose_name="Manzil")
    website = models.URLField(blank=True, verbose_name="Veb-sayt")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Telegram",
        help_text="@ belgisisiz",
    )
    # Brend rasmlari — to'g'ridan-to'g'ri model da saqlanadi
    logo = models.ImageField(
        upload_to="business/logos/",
        null=True,
        blank=True,
        verbose_name="Logo (ikonka / belgi)",
        help_text="Kvadrat, fon yo'q PNG tavsiya etiladi. Masalan: 512×512 px",
    )
    logotype = models.ImageField(
        upload_to="business/logotypes/",
        null=True,
        blank=True,
        verbose_name="Logotip (matnli logo)",
        help_text="Kompaniya nomi yozilgan to'liq logo. Masalan: 1200×400 px",
    )

    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
        verbose_name="Tariflik reja",
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tasdiqlangan biznes",
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
    vehicle_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Transport turi",
        help_text="Masalan: velosiped, mototsikl, avtomobil",
    )
    is_available = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Mavjud",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kuryer profili"
        verbose_name_plural = "Kuryer profillari"

    def __str__(self) -> str:
        return f"Kuryer: {self.user.username}"
