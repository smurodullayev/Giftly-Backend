from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WishlistItem
from .serializers import WishlistItemSerializer


@extend_schema(tags=["Wishlist"])
class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WishlistItemSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return (
            WishlistItem.objects
            .filter(user=self.request.user)
            .select_related("product", "product__business")
            .order_by("-created_at")
        )

    @action(detail=False, methods=["get"], url_path="check")
    def check(self, request):
        product_id = request.query_params.get("product")
        if not product_id:
            return Response(
                {"detail": "?product=<id> parametri majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        exists = WishlistItem.objects.filter(
            user=request.user, product_id=product_id
        ).exists()
        return Response({"product": product_id, "in_wishlist": exists})

    @action(detail=False, methods=["delete"], url_path="remove")
    def remove_by_product(self, request):
        product_id = request.query_params.get("product")
        if not product_id:
            return Response(
                {"detail": "?product=<id> parametri majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = WishlistItem.objects.filter(
            user=request.user, product_id=product_id
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Mahsulot wishlistda topilmadi."},
            status=status.HTTP_404_NOT_FOUND,
        )
