import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.utils.upload_paths


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MediaFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.ImageField(upload_to=apps.utils.upload_paths.media_file_upload, verbose_name="Fayl")),
                ("purpose", models.CharField(
                    choices=[
                        ("user_avatar", "Foydalanuvchi avatari"),
                        ("business_logo", "Biznes logotipi"),
                        ("product_image", "Mahsulot rasmi"),
                        ("other", "Boshqa"),
                    ],
                    db_index=True,
                    default="other",
                    max_length=50,
                    verbose_name="Maqsad",
                )),
                ("original_filename", models.CharField(blank=True, max_length=255, verbose_name="Asl fayl nomi")),
                ("mime_type", models.CharField(blank=True, max_length=100, verbose_name="MIME turi")),
                ("size_bytes", models.PositiveIntegerField(default=0, verbose_name="Hajm (bayt)")),
                ("width", models.PositiveIntegerField(blank=True, null=True, verbose_name="Kenglik (px)")),
                ("height", models.PositiveIntegerField(blank=True, null=True, verbose_name="Balandlik (px)")),
                ("alt_text", models.CharField(blank=True, max_length=255, verbose_name="Alt matn")),
                ("is_primary", models.BooleanField(db_index=True, default=False, verbose_name="Asosiy")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="Tartib")),
                ("object_id", models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name="Bog'liq obyekt ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("content_type", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    to="contenttypes.contenttype",
                    verbose_name="Bog'liq model turi",
                )),
                ("uploaded_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="uploaded_files",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Yuklagan",
                )),
            ],
            options={
                "verbose_name": "Media fayl",
                "verbose_name_plural": "Media fayllar",
                "ordering": ["order", "-is_primary", "created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="mediafile",
            index=models.Index(fields=["content_type", "object_id"], name="media_ct_obj_idx"),
        ),
        migrations.AddIndex(
            model_name="mediafile",
            index=models.Index(fields=["purpose", "content_type", "object_id"], name="media_purpose_ct_obj_idx"),
        ),
    ]
