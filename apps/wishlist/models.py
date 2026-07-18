from django.db import models

from apps.catalog.models import Product
from apps.users.models import User


class WishlistItem(models.Model):
    """
    Foydalanuvchining saqlangan mahsulotlari.
    Bir user bir mahsulotni faqat bir marta saqlaydi (UniqueConstraint).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Foydalanuvchi",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        verbose_name="Mahsulot",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Wishlist elementi"
        verbose_name_plural = "Wishlist"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_wishlist_item",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} → {self.product.title}"
