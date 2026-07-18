import django_filters

from .models import Category, Product


class ProductFilter(django_filters.FilterSet):
    """
    Mahsulotlar uchun kengaytirilgan filtr.

    Misollar:
      ?category=1              — kategoriya ID bo'yicha (o'zi va barcha farzandlari)
      ?category_slug=gullar    — kategoriya slug bo'yicha
      ?occasions=2             — munosabat bo'yicha
      ?price_min=50000         — minimal narx
      ?price_max=500000        — maksimal narx
    """

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # M2M bo'lgani uchun categories__id ishlatiladi
    category = django_filters.NumberFilter(method="filter_by_category")
    category_slug = django_filters.CharFilter(method="filter_by_category_slug")
    occasions = django_filters.NumberFilter(field_name="occasions__id")

    class Meta:
        model = Product
        fields = ["category", "category_slug", "occasions", "price_min", "price_max"]

    def _get_category_ids(self, category: Category) -> list[int]:
        """
        Berilgan kategoriya va uning barcha avlodlarining ID larini qaytaradi.
        3 darajali daraxt uchun rekursiv yig'ish.
        """
        ids = [category.pk]
        for child in category.children.prefetch_related("children").all():
            ids.append(child.pk)
            for grandchild in child.children.all():
                ids.append(grandchild.pk)
        return ids

    def filter_by_category(self, queryset, name, value):
        """?category=<id> — o'sha kategoriya va barcha farzandlarini qamraydi."""
        try:
            cat = Category.objects.get(pk=value)
        except Category.DoesNotExist:
            return queryset.none()
        return queryset.filter(categories__id__in=self._get_category_ids(cat)).distinct()

    def filter_by_category_slug(self, queryset, name, value):
        """?category_slug=gullar — slug bo'yicha filtr."""
        try:
            cat = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            return queryset.none()
        return queryset.filter(categories__id__in=self._get_category_ids(cat)).distinct()
