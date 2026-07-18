from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        # Product.updated_at
        migrations.AddField(
            model_name="product",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        # Product.title — db_index
        migrations.AlterField(
            model_name="product",
            name="title",
            field=models.CharField(db_index=True, max_length=255),
        ),
        # Product.price — db_index
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=12),
        ),
        # Product.is_active — db_index
        migrations.AlterField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(db_index=True, default=True),
        ),
        # Product.created_at — db_index
        migrations.AlterField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # Category: verbose_name (Meta o'zgarishi — migratsiya shart emas lekin izchillik uchun)
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["name"], "verbose_name": "Kategoriya", "verbose_name_plural": "Kategoriyalar"},
        ),
        migrations.AlterModelOptions(
            name="occasion",
            options={"ordering": ["name"], "verbose_name": "Munosabat", "verbose_name_plural": "Munosabatlar"},
        ),
        migrations.AlterModelOptions(
            name="product",
            options={"ordering": ["-created_at"], "verbose_name": "Mahsulot", "verbose_name_plural": "Mahsulotlar"},
        ),
    ]
