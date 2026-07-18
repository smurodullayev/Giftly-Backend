"""
Migration: Category daraxti + Product ko'p kategoriyali

1. Category ga parent (self-FK), slug, icon qo'shiladi
2. UniqueConstraint: bir xil ota ostida nom takrorlanmasin
3. Product.categories (M2M) qo'shiladi
4. Ma'lumotlar ko'chiriladi: har bir product.category → product.categories ga
5. Eski product.category (FK) o'chiriladi
"""

from django.db import migrations, models
import django.db.models.deletion


def copy_category_to_categories(apps, schema_editor):
    """product.category (FK) → product.categories (M2M) ga ko'chiradi."""
    Product = apps.get_model("catalog", "Product")
    for product in Product.objects.filter(category__isnull=False):
        product.categories.add(product.category_id)


def reverse_copy(apps, schema_editor):
    """Orqaga: categories ning birinchisini category ga qaytaradi."""
    Product = apps.get_model("catalog", "Product")
    for product in Product.objects.all():
        first = product.categories.first()
        if first:
            product.category_id = first.pk
            product.save(update_fields=["category_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_tag_and_product_fields"),
    ]

    operations = [
        # 1. Category.parent (o'z-o'ziga FK, ixtiyoriy)
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="catalog.category",
                verbose_name="Yuqori kategoriya",
            ),
        ),

        # 2. Category.slug (avtomatik, unique)
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                help_text="URL uchun — avtomatik to'ldiriladi",
                max_length=120,
                unique=True,
                verbose_name="Slug",
            ),
            preserve_default=False,
        ),

        # 3. Category.icon (ixtiyoriy rasm)
        migrations.AddField(
            model_name="category",
            name="icon",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="categories/icons/",
                verbose_name="Ikonka / rasm",
            ),
        ),

        # 4. UniqueConstraint: (parent, name) juftligi unikal
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_name_per_parent",
            ),
        ),

        # 5. Product.categories (M2M) — yangi field
        migrations.AddField(
            model_name="product",
            name="categories",
            field=models.ManyToManyField(
                blank=True,
                related_name="products",
                to="catalog.category",
                verbose_name="Kategoriyalar",
            ),
        ),

        # 6. Ma'lumotlarni ko'chirish: category → categories
        migrations.RunPython(
            copy_category_to_categories,
            reverse_code=reverse_copy,
        ),

        # 7. Eski product.category (FK) ni o'chirish
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
    ]
