from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0004_category_tree_product_multi_category"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="catalog.product",
                        verbose_name="Mahsulot",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Foydalanuvchi",
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Reyting",
                        help_text="1 dan 5 gacha",
                    ),
                ),
                ("comment", models.TextField(blank=True, verbose_name="Sharh matni")),
                (
                    "is_verified_purchase",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text="Foydalanuvchi ushbu mahsulotni haqiqatan sotib olganmi",
                        verbose_name="Tasdiqlangan xarid",
                    ),
                ),
                ("reply", models.TextField(blank=True, verbose_name="Biznes javobi")),
                ("replied_at", models.DateTimeField(blank=True, null=True, verbose_name="Javob vaqti")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Sharh",
                "verbose_name_plural": "Sharhlar",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_per_product",
            ),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["product", "-created_at"], name="reviews_rev_product_created_idx"),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(fields=["product", "rating"], name="reviews_rev_product_rating_idx"),
        ),
    ]
