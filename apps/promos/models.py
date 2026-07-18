from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.users.models import User


class Coupon(models.Model):
    """
    Chegirma kuponi.

    Turlari:
      percent — foiz chegirma (masalan: 15%)
      fixed   — belgilangan summa chegirma (masalan: 50 000 so'm)

    Cheklovlar:
      min_order_amount   — minimal buyurtma summasi (ixtiyoriy)
      max_discount_amount — foiz chegirma uchun maksimal chegirma summasi (ixtiyoriy)
      max_uses           — umumiy ishlatish limiti (null = cheksiz)
      one_per_user       — har bir user faqat 1 marta ishlatadi
    """

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Foiz (%)"
        FIXED = "fixed", "Belgilangan summa (so'm)"

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Kupon kodi",
        help_text="Katta harf bilan, bo'sh joysiz. Masalan: YOZGI25",
    )
    description = models.CharField(
        max_length=255, blank=True, verbose_name="Tavsif"
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT,
        verbose_name="Chegirma turi",
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Chegirma miqdori",
        help_text="Foiz uchun: 15 (ya'ni 15%). Summa uchun: 50000",
    )
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Maksimal chegirma (so'm)",
        help_text="Faqat foiz turi uchun — chegirma bu summadan oshmasin",
    )
    min_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimal buyurtma summasi",
        help_text="Bu summadan past buyurtmaga qo'llanmaydi",
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maksimal ishlatish soni",
        help_text="Bo'sh qoldirilsa — cheksiz",
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Ishlatilgan soni",
    )
    one_per_user = models.BooleanField(
        default=True,
        verbose_name="Har bir user faqat 1 marta",
    )
    valid_from = models.DateTimeField(verbose_name="Amal qilish boshlanishi")
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Amal qilish tugashi",
        help_text="Bo'sh qoldirilsa — muddatsiz",
    )
    is_active = models.BooleanField(
        default=True, db_index=True, verbose_name="Faol"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kupon"
        verbose_name_plural = "Kuponlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.code} ({self.get_discount_type_display()}: {self.discount_value})"

    # ------------------------------------------------------------------
    # Validatsiya va hisob-kitob
    # ------------------------------------------------------------------

    def is_valid(self, user: User = None, order_amount: Decimal = None) -> tuple[bool, str]:
        """
        Kupon haqiqiyligini tekshiradi.
        Qaytaradi: (is_valid: bool, error_message: str)
        """
        now = timezone.now()

        if not self.is_active:
            return False, "Kupon faol emas."

        if now < self.valid_from:
            return False, "Kupon hali kuchga kirmagan."

        if self.valid_until and now > self.valid_until:
            return False, "Kupon muddati tugagan."

        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False, "Kupon ishlatish limiti tugagan."

        if self.min_order_amount and order_amount and order_amount < self.min_order_amount:
            return False, (
                f"Kupon faqat {self.min_order_amount:,.0f} so'mdan yuqori buyurtmaga qo'llanadi."
            )

        if user and self.one_per_user:
            if CouponUsage.objects.filter(coupon=self, user=user).exists():
                return False, "Siz bu kuponni allaqachon ishlatgansiz."

        return True, ""

    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        """Chegirma summasini hisoblaydi."""
        if self.discount_type == self.DiscountType.PERCENT:
            discount = order_amount * self.discount_value / 100
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value

        # Chegirma buyurtma summasidan oshmasin
        return min(discount, order_amount)


class CouponUsage(models.Model):
    """Kupon ishlatilish tarixi — kim, qachon, qancha chegirma oldi."""

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name="Kupon",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
        verbose_name="Foydalanuvchi",
    )
    discount_applied = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Qo'llanilgan chegirma",
    )
    order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Buyurtma summasi",
    )
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Ishlatilgan vaqt")

    class Meta:
        verbose_name = "Kupon ishlatilishi"
        verbose_name_plural = "Kupon tarixi"
        ordering = ["-used_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "user"],
                name="unique_coupon_per_user",
                condition=models.Q(coupon__one_per_user=True),
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} — {self.coupon.code} ({self.discount_applied} so'm)"
