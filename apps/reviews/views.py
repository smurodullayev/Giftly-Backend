from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review
from .permissions import IsProductBusinessOwner, IsReviewAuthorOrAdmin
from .serializers import (
    BusinessReplySerializer,
    ProductRatingSummarySerializer,
    ReviewReadSerializer,
    ReviewUpdateSerializer,
    ReviewWriteSerializer,
)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    /api/v1/reviews/

    Filtrlar:
      ?product=1         — mahsulot bo'yicha
      ?rating=5          — reyting bo'yicha
      ?verified=true     — faqat tasdiqlangan xaridlar
      ?ordering=-rating  — reyting bo'yicha
      ?ordering=-created_at — yangiligi bo'yicha (standart)

    Qo'shimcha endpointlar:
      POST   /reviews/{id}/reply/    → biznes javobi (faqat mahsulot egasi)
      DELETE /reviews/{id}/reply/    → javobni o'chirish (faqat mahsulot egasi)
      GET    /reviews/summary/       → ?product=<id> bo'yicha reyting xulosasi
    """

    search_fields = ["comment", "user__username"]
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]
    filterset_fields = {
        "product": ["exact"],
        "rating": ["exact", "gte", "lte"],
        "is_verified_purchase": ["exact"],
    }

    def get_queryset(self):
        return (
            Review.objects
            .select_related("user", "product", "product__business")
            .order_by("-created_at")
        )

    def get_permissions(self):
        if self.action in ("list", "retrieve", "summary"):
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsReviewAuthorOrAdmin()]
        if self.action in ("reply", "delete_reply"):
            return [permissions.IsAuthenticated(), IsProductBusinessOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReviewReadSerializer
        if self.action in ("update", "partial_update"):
            return ReviewUpdateSerializer
        if self.action in ("reply", "delete_reply"):
            return BusinessReplySerializer
        return ReviewWriteSerializer

    # ------------------------------------------------------------------
    # Biznes javobi
    # ------------------------------------------------------------------

    @action(detail=True, methods=["post"], url_path="reply")
    def reply(self, request, pk=None):
        """
        POST /api/v1/reviews/{id}/reply/
        Biznes egasi sharhga javob qoldiradi.
        """
        review = self.get_object()
        serializer = BusinessReplySerializer(
            review, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        review.reply = serializer.validated_data["reply"]
        review.replied_at = timezone.now()
        review.save(update_fields=["reply", "replied_at"])
        return Response(ReviewReadSerializer(review, context={"request": request}).data)

    @action(detail=True, methods=["delete"], url_path="reply")
    def delete_reply(self, request, pk=None):
        """
        DELETE /api/v1/reviews/{id}/reply/
        Biznes egasi o'z javobini o'chiradi.
        """
        review = self.get_object()
        review.reply = ""
        review.replied_at = None
        review.save(update_fields=["reply", "replied_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # Reyting xulosasi
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """
        GET /api/v1/reviews/summary/?product=<id>
        Mahsulot reytingi xulosasi: o'rtacha, soni, 1-5 taqsimot.
        """
        product_id = request.query_params.get("product")
        if not product_id:
            return Response(
                {"detail": "?product=<id> parametri majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Review.objects.filter(product_id=product_id)
        agg = qs.aggregate(avg_rating=Avg("rating"), review_count=Count("id"))

        # 1★ dan 5★ gacha soni
        breakdown = {}
        for star in range(1, 6):
            breakdown[str(star)] = qs.filter(rating=star).count()

        verified_count = qs.filter(is_verified_purchase=True).count()

        data = {
            "product_id": int(product_id),
            "avg_rating": round(agg["avg_rating"] or 0, 2),
            "review_count": agg["review_count"],
            "rating_breakdown": breakdown,
            "verified_count": verified_count,
        }
        serializer = ProductRatingSummarySerializer(data)
        return Response(serializer.data)
