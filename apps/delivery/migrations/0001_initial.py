import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DeliveryZone",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Zona nomi")),
                (
                    "keywords",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        size=None,
                        verbose_name="Kalit so'zlar",
                    ),
                ),
                (
                    "base_fee",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Asosiy narx (so'm)",
                    ),
                ),
                (
                    "per_kg_fee",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=8,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="1 kg uchun narx (so'm)",
                    ),
                ),
                ("free_above_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="Bepul yetkazish limiti (so'm)")),
                ("is_default", models.BooleanField(default=False, verbose_name="Standart zona")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="Faol")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Tartib")),
            ],
            options={
                "verbose_name": "Yetkazib berish zonasi",
                "verbose_name_plural": "Yetkazib berish zonalari",
                "ordering": ["sort_order", "name"],
            },
        ),
    ]
