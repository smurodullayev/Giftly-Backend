import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Mahsulotlar uchun kengaytirilgan filtr.

    Misollar:
      ?category=1
      ?occasions=2
      ?price_min=50000&price_max=500000
      ?search=gul           (title va description bo'yicha)
      ?ordering=-price      (narx bo'yicha kamayish tartibida)
    """

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category__id")
    occasions = django_filters.NumberFilter(field_name="occasions__id")

    class Meta:
        model = Product
        fields = ["category", "occasions", "price_min", "price_max"]
