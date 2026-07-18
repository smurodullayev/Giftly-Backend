from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Category, Occasion, Product, Tag
from .permissions import IsAdminOrReadOnly, IsBusinessOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
    OccasionSerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    TagSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/categories/
    O'qish — hammaga. Yaratish/o'zgartirish/o'chirish — faqat admin.

    Qo'shimcha endpoint:
      GET /api/v1/catalog/categories/tree/
        — 1-daraja (root) kategoriyalar va barcha farzandlarini nested ko'rinishda qaytaradi.
    """

    queryset = Category.objects.select_related("parent").prefetch_related(
        "children", "children__children"
    )
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """
        GET /api/v1/catalog/categories/tree/
        Faqat 1-daraja (parent=None) kategoriyalarni,
        2 va 3-daraja farzandlari bilan qaytaradi.
        """
        roots = (
            Category.objects
            .filter(parent__isnull=True)
            .prefetch_related("children__children")
            .order_by("name")
        )
        serializer = CategoryTreeSerializer(
            roots, many=True, context={"request": request}
        )
        return Response(serializer.data)


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


class TagViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/tags/
    O'qish — hammaga. Yaratish/o'zgartirish/o'chirish — faqat admin.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    """
    /api/v1/catalog/products/

    Filtrlar:
      ?category=1               — kategoriya ID (farzandlari bilan)
      ?category_slug=gullar     — kategoriya slug bo'yicha
      ?occasions=2              — munosabat bo'yicha
      ?price_min=50000          — minimal narx
      ?price_max=500000         — maksimal narx
      ?search=gul               — title/description bo'yicha qidiruv
      ?ordering=-price          — narx bo'yicha (kamayish)
      ?ordering=created_at      — vaqt bo'yicha (o'sish)
    """

    permission_classes = [IsBusinessOwnerOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["title", "description", "sku", "tags__name"]
    ordering_fields = ["price", "created_at", "title", "stock"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Product.objects
            .select_related("business")
            .prefetch_related("categories", "categories__parent", "occasions", "tags")
        )
        user = self.request.user
        # Autentifikatsiyasiz yoki oddiy user — faqat aktiv mahsulotlar
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
