from rest_framework import permissions, viewsets

from .filters import ProductFilter
from .models import Category, Occasion, Product
from .permissions import IsAdminOrReadOnly, IsBusinessOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    OccasionSerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/categories/
    O'qish — hammaga. Yaratish/o'zgartirish/o'chirish — faqat admin.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


class OccasionViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/occasions/
    O'qish — hammaga. Yaratish/o'zgartirish/o'chirish — faqat admin.
    """

    queryset = Occasion.objects.all()
    serializer_class = OccasionSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/products/

    Filtrlar:
      ?category=1          — kategoriya bo'yicha
      ?occasions=2         — munosabat bo'yicha
      ?price_min=50000     — minimal narx
      ?price_max=500000    — maksimal narx
      ?search=gul          — title/description bo'yicha qidiruv
      ?ordering=-price     — narx bo'yicha (kamayish)
      ?ordering=created_at — vaqt bo'yicha (o'sish)
    """

    permission_classes = [IsBusinessOwnerOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["title", "description"]
    ordering_fields = ["price", "created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Product.objects
            .select_related("business", "category")
            .prefetch_related("occasions")
        )
        # Autentifikatsiyasiz yoki oddiy user — faqat aktiv mahsulotlar
        user = self.request.user
        if not user.is_authenticated or user.role not in ("business", "admin"):
            return qs.filter(is_active=True)
        # Business user — faqat o'z mahsulotlari (aktiv + nofaol)
        if user.role == "business":
            return qs.filter(business=user)
        # Admin — hammasi
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ProductReadSerializer
        return ProductWriteSerializer
