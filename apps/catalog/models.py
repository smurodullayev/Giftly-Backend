from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.users.models import User


class Category(models.Model):
    """
    3 darajali o'z-o'ziga bog'liq kategoriya daraxti.
    Daraja 1: Gullar
    Daraja 2: Gullar → Atirgullar
    Daraja 3: Gullar → Atirgullar → Qizil atirgullar
    """

    name = models.CharField(max_length=100, verbose_name="Nomi")
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL uchun — avtomatik to'ldiriladi",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="Yuqori kategoriya",
    )
    icon = models.ImageField(
        upload_to="categories/icons/",
        null=True,
        blank=True,
        verbose_name="Ikonka / rasm",
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]
        # Bir xil ota ostida nom takrorlanmasin
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_name_per_parent",
            )
        ]

    def __str__(self) -> str:
        return self.full_path

    # ------------------------------------------------------------------
    # Yordamchi xususiyatlar
    # ------------------------------------------------------------------

    @property
    def level(self) -> int:
        """1-darajali (root) = 1, eng chuqur = 3."""
        depth = 1
        node = self
        while node.parent_id:
            depth += 1
            node = node.parent
        return depth

    @property
    def full_path(self) -> str:
        """Admin panelda chiroyli ko'rinish: Gullar → Atirgullar"""
        parts = [self.name]
        node = self
        while node.parent_id:
            node = node.parent
            parts.append(node.name)
        return " → ".join(reversed(parts))

    @property
    def root(self) -> "Category":
        """Ildiz (1-daraja) kategoriyani qaytaradi."""
        node = self
        while node.parent_id:
            node = node.parent
        return node

    # ------------------------------------------------------------------
    # Validatsiya va saqlash
    # ------------------------------------------------------------------

    def _get_depth_from_parent(self) -> int:
        """Ota tomonidan hisoblangan chuqurlik (parent + 1)."""
        if not self.parent_id:
            return 1
        depth = 1
        node = self.parent
        while node.parent_id:
            depth += 1
            node = node.parent
        return depth + 1

    def clean(self):
        # Maksimal chuqurlik: 3
        if self.parent_id and self._get_depth_from_parent() > 3:
            raise ValidationError(
                "Kategoriya daraxti 3 darajadan chuqur bo'la olmaydi."
            )
        # O'z-o'ziga bog'lanishni oldini olish
        if self.pk and self.parent_id == self.pk:
            raise ValidationError(
                "Kategoriya o'zini ota sifatida ko'rsata olmaydi."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        # Slug avtomatik generatsiya
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


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

    # Katalog — M2M: bitta mahsulot bir necha kategoriyaga tegishli bo'lishi mumkin
    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
        verbose_name="Kategoriyalar",
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
