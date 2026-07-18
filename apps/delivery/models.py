from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models


class DeliveryZone(models.Model):
    """
    Yetkazib berish zonasi.

    Qanday ishlaydi:
    - Har bir zona uchun `keywords` ro'yxati belgilanadi (shahar/viloyat nomlari).
    - Xaridor manzilida shu kalit so'zlardan biri topilsa — o'sha zona narxi qo'llanadi.
    - Agar hech qaysi zona mos kelmasa — `is_default=True` bo'lgan zona qo'llanadi.

    Narx formulasi:
      delivery_fee = base_fee + (weight_kg * per_kg_fee)
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Zona nomi")
    keywords = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Kalit so'zlar",
        help_text="Manzildan qidiriladigan so'zlar. Masalan: ['toshkent', 'tashkent', 'yunusobod']",
    )
    base_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Asosiy narx (so'm)",
        help_text="Og'irlikdan qat'i nazar olinadigan minimal narx",
    )
    per_kg_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="1 kg uchun narx (so'm)",
        help_text="0 bo'lsa — og'irlik hisobga olinmaydi",
    )
    free_above_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Bepul yetkazish limiti (so'm)",
        help_text="Buyurtma shu summadan yuqori bo'lsa yetkazish bepul",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Standart zona",
        help_text="Hech qaysi kalit so'z mos kelmasa shu zona qo'llanadi",
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Faol")
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Tartib",
        help_text="Kichik raqam — avval tekshiriladi",
    )

    class Meta:
        verbose_name = "Yetkazib berish zonasi"
        verbose_name_plural = "Yetkazib berish zonalari"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return f"{self.name} — {self.base_fee:,.0f} so'm + {self.per_kg_fee:,.0f} so'm/kg"

    def calculate_fee(self, weight_grams: int, order_amount=None) -> "Decimal":
        """
        Yetkazib berish narxini hisoblaydi.
        weight_grams: mahsulot og'irligi grammda
        order_amount: buyurtma summasi (bepul limit tekshiruvi uchun)
        """
        from decimal import Decimal

        # Bepul yetkazish tekshiruvi
        if self.free_above_amount and order_amount and order_amount >= self.free_above_amount:
            return Decimal("0")

        weight_kg = Decimal(weight_grams) / 1000
        return self.base_fee + (weight_kg * self.per_kg_fee)
