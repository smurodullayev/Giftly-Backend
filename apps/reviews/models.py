from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.catalog.models import Product
from apps.users.models import User


class Review(models.Model):
    """
    Mahsulot sharhi va reytingi.

    Qoidalar:
    - Faqat 'delivered' statusli buyurtmasi bo'lgan user yoza oladi.
    - Har bir user har bir mahsulotga faqat 1 ta sharh yoza oladi.
    - is_verified_purchase — saqlashda avtomatik tekshiriladi.
    - Biznes egasi reply (javob) qoldira oladi.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Mahsulot",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Foydalanuvchi",
    )

    # Reyting: 1 (yomon) — 5 (a'lo)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Reyting",
        help_text="1 dan 5 gacha",
    )
    comment = models.TextField(blank=True, verbose_name="Sharh matni")

    # Yetkazilgan buyurtma orqali tekshirilgan xaridor
    is_verified_purchase = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Tasdiqlangan xarid",
        help_text="Foydalanuvchi ushbu mahsulotni haqiqatan sotib olganmi",
    )

    # Biznes javobi
    reply = models.TextField(blank=True, verbose_name="Biznes javobi")
    replied_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Javob vaqti"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_per_product",
            )
        ]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["product", "rating"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} → {self.product.title} ({self.rating}★)"

    def save(self, *args, **kwargs):
        # Yetkazilgan buyurtma borligini tekshirish
        from apps.leads.models import Order
        self.is_verified_purchase = Order.objects.filter(
            lead__user=self.user,
            lead__product=self.product,
            status=Order.Status.DELIVERED,
        ).exists()
        super().save(*args, **kwargs)
