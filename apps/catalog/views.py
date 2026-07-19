from django.db.models import Avg, Count
from drf_spectacular.utils import extend_schema, extend_schema_view
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


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], summary="List categories"),
    retrieve=extend_schema(tags=["Catalog"], summary="Retrieve a category"),
    create=extend_schema(tags=["Catalog"], summary="Create a category"),
    update=extend_schema(tags=["Catalog"], summary="Update a category"),
    partial_update=extend_schema(tags=["Catalog"], summary="Partially update a category"),
    destroy=extend_schema(tags=["Catalog"], summary="Delete a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("parent").prefetch_related(
        "children", "children__children"
    )
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]

    @extend_schema(tags=["Catalog"], summary="Get full category tree")
    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
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


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], summary="List occasions"),
    retrieve=extend_schema(tags=["Catalog"], summary="Retrieve an occasion"),
    create=extend_schema(tags=["Catalog"], summary="Create an occasion"),
    update=extend_schema(tags=["Catalog"], summary="Update an occasion"),
    partial_update=extend_schema(tags=["Catalog"], summary="Partially update an occasion"),
    destroy=extend_schema(tags=["Catalog"], summary="Delete an occasion"),
)
class OccasionViewSet(viewsets.ModelViewSet):
    queryset = Occasion.objects.all()
    serializer_class = OccasionSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], summary="List tags"),
    retrieve=extend_schema(tags=["Catalog"], summary="Retrieve a tag"),
    create=extend_schema(tags=["Catalog"], summary="Create a tag"),
    update=extend_schema(tags=["Catalog"], summary="Update a tag"),
    partial_update=extend_schema(tags=["Catalog"], summary="Partially update a tag"),
    destroy=extend_schema(tags=["Catalog"], summary="Delete a tag"),
)
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "slug"]
    ordering_fields = ["name"]
    ordering = ["name"]


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], summary="List products"),
    retrieve=extend_schema(tags=["Catalog"], summary="Retrieve a product"),
    create=extend_schema(tags=["Catalog"], summary="Create a product"),
    update=extend_schema(tags=["Catalog"], summary="Update a product"),
    partial_update=extend_schema(tags=["Catalog"], summary="Partially update a product"),
    destroy=extend_schema(tags=["Catalog"], summary="Delete a product"),
)
class ProductViewSet(viewsets.ModelViewSet):
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
            .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
        )
        user = self.request.user
        if not user.is_authenticated or user.role not in ("business", "admin"):
            return qs.filter(is_active=True)
        if user.role == "business":
            return qs.filter(business=user)
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ProductReadSerializer
        return ProductWriteSerializer
