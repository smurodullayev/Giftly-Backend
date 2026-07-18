from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Occasion, Product
from .serializers import CategorySerializer, OccasionSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OccasionViewSet(viewsets.ModelViewSet):
    queryset = Occasion.objects.all()
    serializer_class = OccasionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """Kategoriya va bayram (occasion) bo'yicha filtrlash:
    /api/catalog/products/?category=1&occasions=2
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "occasions"]
