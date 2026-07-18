from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_add_updated_at_and_indexes"),
    ]

    operations = [
        # Tag modeli
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True, verbose_name="Nomi")),
                ("slug", models.SlugField(blank=True, max_length=60, unique=True)),
            ],
            options={
                "verbose_name": "Teg",
                "verbose_name_plural": "Teglar",
                "ordering": ["name"],
            },
        ),
        # Product.slug
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(
                blank=True,
                db_index=True,
                help_text="URL uchun — avtomatik to'ldiriladi",
                max_length=300,
                unique=True,
                verbose_name="Slug",
            ),
        ),
        # Product.sale_price
        migrations.AddField(
            model_name="product",
            name="sale_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Chegirma bo'lmasa bo'sh qoldiring",
                max_digits=12,
                null=True,
                verbose_name="Chegirma narxi",
            ),
        ),
        # Product.sku
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name="SKU / Mahsulot kodi",
            ),
        ),
        # Product.stock
        migrations.AddField(
            model_name="product",
            name="stock",
            field=models.PositiveIntegerField(default=0, verbose_name="Qoldiq (dona)"),
        ),
        # Product.min_order_qty
        migrations.AddField(
            model_name="product",
            name="min_order_qty",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Minimal buyurtma miqdori"),
        ),
        # Product.weight_grams
        migrations.AddField(
            model_name="product",
            name="weight_grams",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Kuryer hisob-kitobi uchun",
                null=True,
                verbose_name="Og'irlik (gramm)",
            ),
        ),
        # Product.tags (M2M)
        migrations.AddField(
            model_name="product",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                to="catalog.tag",
                verbose_name="Teglar",
            ),
        ),
    ]
