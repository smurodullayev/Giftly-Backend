from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_add_updated_at_and_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="Tug'ilgan sana"),
        ),
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.CharField(blank=True, max_length=500, verbose_name="Manzil"),
        ),
        migrations.AddField(
            model_name="user",
            name="telegram",
            field=models.CharField(
                blank=True,
                help_text="@ belgisisiz, masalan: username",
                max_length=100,
                verbose_name="Telegram",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="bio",
            field=models.TextField(blank=True, verbose_name="Qisqacha ma'lumot"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Telefon yoki email orqali tasdiqlangan hisob",
                verbose_name="Tasdiqlangan",
            ),
        ),
        # BusinessProfile yangi fieldlar
        migrations.AddField(
            model_name="businessprofile",
            name="phone",
            field=models.CharField(
                blank=True,
                help_text="Kompaniya bog'lanish raqami",
                max_length=20,
                verbose_name="Biznes telefon",
            ),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="address",
            field=models.CharField(blank=True, max_length=500, verbose_name="Manzil"),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="website",
            field=models.URLField(blank=True, verbose_name="Veb-sayt"),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="instagram_url",
            field=models.URLField(blank=True, verbose_name="Instagram URL"),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="telegram_username",
            field=models.CharField(
                blank=True,
                help_text="@ belgisisiz",
                max_length=100,
                verbose_name="Telegram",
            ),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="is_verified",
            field=models.BooleanField(
                db_index=True,
                default=False,
                verbose_name="Tasdiqlangan biznes",
            ),
        ),
    ]
