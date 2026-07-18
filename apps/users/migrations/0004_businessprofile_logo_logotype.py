from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_user_new_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="businessprofile",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="business/logos/",
                verbose_name="Logo (ikonka / belgi)",
                help_text="Kvadrat, fon yo'q PNG tavsiya etiladi. Masalan: 512×512 px",
            ),
        ),
        migrations.AddField(
            model_name="businessprofile",
            name="logotype",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="business/logotypes/",
                verbose_name="Logotip (matnli logo)",
                help_text="Kompaniya nomi yozilgan to'liq logo. Masalan: 1200×400 px",
            ),
        ),
    ]
