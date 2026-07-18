from django.db import models
from apps.users.models import User
from apps.catalog.models import Product


class Lead(models.Model):
    """MVP: foydalanuvchi tanlangan mahsulot bo'yicha so'rov yuboradi."""
    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        CONTACTED = "contacted", "Bog'lanildi"
        CLOSED = "closed", "Yopilgan"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="leads")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lead #{self.id} — {self.product.title}"


class Order(models.Model):
    """Keyingi bosqich: to'lov va kuryer moduli bilan bog'lanadi."""
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'landi"
        IN_DELIVERY = "in_delivery", "Yetkazilmoqda"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="order")
    courier = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deliveries", limit_choices_to={"role": "courier"}
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.status})"
