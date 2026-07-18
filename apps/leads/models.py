from django.db import models

from apps.catalog.models import Product
from apps.users.models import User


class Lead(models.Model):
    """Foydalanuvchi tanlangan mahsulot bo'yicha so'rov yuboradi."""

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        CONTACTED = "contacted", "Bog'lanildi"
        CLOSED = "closed", "Yopilgan"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="Foydalanuvchi",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="leads",
        verbose_name="Mahsulot",
    )
    message = models.TextField(blank=True, verbose_name="Xabar")
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Bog'lanish raqami",
        help_text="Profildan farqli bo'lsa ko'rsating",
    )
    preferred_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kerakli yetkazish sanasi",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leadlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Lead #{self.pk} — {self.product.title}"


class Order(models.Model):
    """To'lov va kuryer moduli bilan bog'lanadi."""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'landi"
        IN_DELIVERY = "in_delivery", "Yetkazilmoqda"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Naqd pul"
        CARD = "card", "Karta"
        TRANSFER = "transfer", "Bank o'tkazma"
        ONLINE = "online", "Online to'lov"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "To'lanmagan"
        PAID = "paid", "To'langan"
        REFUNDED = "refunded", "Qaytarilgan"

    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="order",
        verbose_name="Lead",
    )
    courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
        limit_choices_to={"role": User.Role.COURIER},
        verbose_name="Kuryer",
    )

    # Yetkazish
    delivery_address = models.TextField(verbose_name="Yetkazish manzili")
    notes = models.TextField(blank=True, verbose_name="Izoh / qo'shimcha so'rov")
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name="Kuzatuv raqami",
    )
    estimated_delivery = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Taxminiy yetkazish vaqti",
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Haqiqiy yetkazish vaqti",
    )

    # Narx (buyurtma paytidagi snapshot — mahsulot narxi o'zgarsa ham saqlanadi)
    price_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Buyurtma paytidagi narx",
    )
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Yetkazish narxi",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Jami summa",
        help_text="price_snapshot + delivery_fee — avtomatik hisoblanadi",
    )

    # To'lov
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name="To'lov usuli",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
        verbose_name="To'lov holati",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # total_amount har doim avtomatik hisoblanadi
        self.total_amount = self.price_snapshot + self.delivery_fee
        super().save(*args, **kwargs)
