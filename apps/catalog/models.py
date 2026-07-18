from django.db import models

from apps.users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Occasion(models.Model):
    """Munosabat/bayram turi: tug'ilgan kun, to'y, Yangi yil va h.k."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Munosabat"
        verbose_name_plural = "Munosabatlar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    business = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role": User.Role.BUSINESS},
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    occasions = models.ManyToManyField(Occasion, related_name="products", blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
