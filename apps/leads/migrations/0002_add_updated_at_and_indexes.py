from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0001_initial"),
    ]

    operations = [
        # Lead.updated_at
        migrations.AddField(
            model_name="lead",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # Lead.status — db_index
        migrations.AlterField(
            model_name="lead",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "Yangi"),
                    ("contacted", "Bog'lanildi"),
                    ("closed", "Yopilgan"),
                ],
                db_index=True,
                default="new",
                max_length=20,
            ),
        ),
        # Lead.created_at — db_index
        migrations.AlterField(
            model_name="lead",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # Order.updated_at
        migrations.AddField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # Order.status — db_index
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Kutilmoqda"),
                    ("paid", "To'landi"),
                    ("in_delivery", "Yetkazilmoqda"),
                    ("delivered", "Yetkazildi"),
                    ("cancelled", "Bekor qilindi"),
                ],
                db_index=True,
                default="pending",
                max_length=20,
            ),
        ),
        # Model options
        migrations.AlterModelOptions(
            name="lead",
            options={"ordering": ["-created_at"], "verbose_name": "Lead", "verbose_name_plural": "Leadlar"},
        ),
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"], "verbose_name": "Buyurtma", "verbose_name_plural": "Buyurtmalar"},
        ),
    ]
