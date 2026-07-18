import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0002_add_updated_at_and_indexes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Lead yangi fieldlar
        migrations.AddField(
            model_name="lead",
            name="contact_phone",
            field=models.CharField(
                blank=True,
                help_text="Profildan farqli bo'lsa ko'rsating",
                max_length=20,
                verbose_name="Bog'lanish raqami",
            ),
        ),
        migrations.AddField(
            model_name="lead",
            name="preferred_delivery_date",
            field=models.DateField(blank=True, null=True, verbose_name="Kerakli yetkazish sanasi"),
        ),
        # Order yangi fieldlar
        migrations.AddField(
            model_name="order",
            name="delivery_address",
            field=models.TextField(default="", verbose_name="Yetkazish manzili"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="notes",
            field=models.TextField(blank=True, verbose_name="Izoh / qo'shimcha so'rov"),
        ),
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(blank=True, db_index=True, max_length=100, verbose_name="Kuzatuv raqami"),
        ),
        migrations.AddField(
            model_name="order",
            name="estimated_delivery",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Taxminiy yetkazish vaqti"),
        ),
        migrations.AddField(
            model_name="order",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Haqiqiy yetkazish vaqti"),
        ),
        migrations.AddField(
            model_name="order",
            name="price_snapshot",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Mahsulot narxi o'zgarsa ham saqlanib qoladi",
                max_digits=12,
                verbose_name="Buyurtma paytidagi narx",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="Yetkazish narxi",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="price_snapshot + delivery_fee — avtomatik hisoblanadi",
                max_digits=12,
                verbose_name="Jami summa",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cash", "Naqd pul"),
                    ("card", "Karta"),
                    ("transfer", "Bank o'tkazma"),
                    ("online", "Online to'lov"),
                ],
                default="cash",
                max_length=20,
                verbose_name="To'lov usuli",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("unpaid", "To'lanmagan"),
                    ("paid", "To'langan"),
                    ("refunded", "Qaytarilgan"),
                ],
                db_index=True,
                default="unpaid",
                max_length=20,
                verbose_name="To'lov holati",
            ),
        ),
        migrations.AlterModelOptions(
            name="order",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Buyurtma",
                "verbose_name_plural": "Buyurtmalar",
            },
        ),
    ]
