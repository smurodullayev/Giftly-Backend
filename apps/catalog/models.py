from django.db import models
from django.utils.text import slugify

from apps.users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Occasion(models.Model):
    """Munosabat/bayram turi: tug'ilgan kun, to'y, Yangi yil va h.k."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")

    class Meta:
        verbose_name = "Munosabat"
        verbose_name_plural = "Munosabatlar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Mahsulot teglari — erkin kalit so'zlar."""

    name = models.CharField(max_length=50, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        verbose_name = "Teg"
        verbose_name_plural = "Teglar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    business = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role": User.Role.BUSINESS},
        verbose_name="Biznes",
    )
    title = models.CharField(max_length=255, db_index=True, verbose_name="Sarlavha")
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug",
        help_text="URL uchun — avtomatik to'ldiriladi",
    )
    description = models.TextField(blank=True, verbose_name="Tavsif")

    # Narx
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        db_index=True,
        verbose_name="Narx (so'm)",
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Chegirma narxi",
        help_text="Chegirma bo'lmasa bo'sh qoldiring",
    )

    # Katalog
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Kategoriya",
    )
    occasions = models.ManyToManyField(
        Occasion,
        related_name="products",
        blank=True,
        verbose_name="Munosabatlar",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        blank=True,
        verbose_name="Teglar",
    )

    # Inventar
    sku = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="SKU / Mahsulot kodi",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Qoldiq (dona)")
    min_order_qty = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Minimal buyurtma miqdori",
    )

    # Kuryer uchun
    weight_grams = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Og'irlik (gramm)",
        help_text="Kuryer hisob-kitobi uchun",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Aktiv",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        """Joriy narx: chegirma bo'lsa chegirma narxi, aks holda asosiy narx."""
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def is_in_stock(self) -> bool:
        return self.stock >= self.min_order_qty
