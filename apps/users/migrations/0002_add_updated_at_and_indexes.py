import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        # User.updated_at
        migrations.AddField(
            model_name="user",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # User.role — db_index (CharField'ga index qo'shamiz)
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("user", "Foydalanuvchi"),
                    ("business", "Biznes"),
                    ("courier", "Kuryer"),
                    ("admin", "Admin"),
                ],
                db_index=True,
                default="user",
                max_length=20,
            ),
        ),
        # User.phone — db_index
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, db_index=True, max_length=20),
        ),
        # BusinessProfile.updated_at
        migrations.AddField(
            model_name="businessprofile",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # BusinessProfile.subscription_plan — choices to'plami o'zgardi
        migrations.AlterField(
            model_name="businessprofile",
            name="subscription_plan",
            field=models.CharField(
                choices=[("free", "Bepul"), ("basic", "Asosiy"), ("pro", "Pro")],
                default="free",
                max_length=20,
            ),
        ),
        # CourierProfile.updated_at
        migrations.AddField(
            model_name="courierprofile",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # CourierProfile.is_available — db_index
        migrations.AlterField(
            model_name="courierprofile",
            name="is_available",
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
