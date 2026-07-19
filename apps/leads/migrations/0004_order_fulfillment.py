from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0003_lead_order_expanded"),
    ]

    operations = [
        # 1. fulfillment_type maydoni qo'shiladi
        migrations.AddField(
            model_name="order",
            name="fulfillment_type",
            field=models.CharField(
                max_length=20,
                choices=[("delivery", "Yetkazib berish"), ("pickup", "O'zim olib ketaman")],
                default="delivery",
                verbose_name="Yetkazish turi",
            ),
        ),
        # 2. delivery_address endi null/blank bo'lishi mumkin (pickup uchun)
        migrations.AlterField(
            model_name="order",
            name="delivery_address",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Yetkazish manzili",
                help_text="Pickup tanlanganda bo'sh qoldiriladi",
            ),
        ),
        # 3. Status choices yangilanadi
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("pending",     "Kutilmoqda"),
                    ("paid",        "To'landi"),
                    ("in_progress", "Tayyorlanmoqda"),
                    ("completed",   "Yakunlandi"),
                    ("cancelled",   "Bekor qilindi"),
                ],
                default="pending",
                db_index=True,
                verbose_name="Holat",
            ),
        ),
    ]
