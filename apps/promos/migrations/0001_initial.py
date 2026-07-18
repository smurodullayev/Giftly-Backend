import decimal
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=50, unique=True, verbose_name="Kupon kodi")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="Tavsif")),
                ("discount_type", models.CharField(
                    choices=[("percent", "Foiz (%)"), ("fixed", "Belgilangan summa (so'm)")],
                    default="percent",
                    max_length=10,
                    verbose_name="Chegirma turi",
                )),
                ("discount_value", models.DecimalField(
                    decimal_places=2,
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))],
                    verbose_name="Chegirma miqdori",
                )),
                ("max_discount_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="Maksimal chegirma (so'm)")),
                ("min_order_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="Minimal buyurtma summasi")),
                ("max_uses", models.PositiveIntegerField(blank=True, null=True, verbose_name="Maksimal ishlatish soni")),
                ("used_count", models.PositiveIntegerField(default=0, verbose_name="Ishlatilgan soni")),
                ("one_per_user", models.BooleanField(default=True, verbose_name="Har bir user faqat 1 marta")),
                ("valid_from", models.DateTimeField(verbose_name="Amal qilish boshlanishi")),
                ("valid_until", models.DateTimeField(blank=True, null=True, verbose_name="Amal qilish tugashi")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="Faol")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Kupon",
                "verbose_name_plural": "Kuponlar",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CouponUsage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("coupon", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="usages", to="promos.coupon", verbose_name="Kupon")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="coupon_usages", to=settings.AUTH_USER_MODEL, verbose_name="Foydalanuvchi")),
                ("discount_applied", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Qo'llanilgan chegirma")),
                ("order_amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Buyurtma summasi")),
                ("used_at", models.DateTimeField(auto_now_add=True, verbose_name="Ishlatilgan vaqt")),
            ],
            options={
                "verbose_name": "Kupon ishlatilishi",
                "verbose_name_plural": "Kupon tarixi",
                "ordering": ["-used_at"],
            },
        ),
    ]
