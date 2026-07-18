from django.db import models

from apps.catalog.models import Product
from apps.users.models import User


class Lead(models.Model):
    """Foydalanuvchi tanlangan mahsulot bo'yicha so'rov yuboradi."""

    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        CONTACTED = "contacted", "Bog'lanildi"
        CLOSED = "closed", "Yopilgan"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="leads")
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
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

    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="order")
    courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
        limit_choices_to={"role": User.Role.COURIER},
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.get_status_display()})"
