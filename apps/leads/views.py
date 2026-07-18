from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Lead, Order
from .permissions import IsLeadOwnerOrProductBusiness, IsOrderParticipantOrAdmin
from .serializers import LeadSerializer, LeadStatusSerializer, OrderSerializer


class LeadViewSet(viewsets.ModelViewSet):
    """
    /api/v1/leads/leads/

    - User: faqat o'z leadlarini yaratadi va ko'radi.
    - Business: o'z mahsulotlariga kelgan leadlarni ko'radi, statusini yangilaydi.
    - Admin: barchasini ko'radi va boshqaradi.

    Status yangilash: PATCH /api/v1/leads/leads/{id}/update-status/
    """

    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Lead.objects.select_related(
            "user", "product", "product__business", "product__category"
        )
        if user.is_staff or user.role == "admin":
            return qs.all()
        if user.role == "business":
            return qs.filter(product__business=user)
        # Oddiy foydalanuvchi — faqat o'z leadlari
        return qs.filter(user=user)

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy", "update_status"):
            return [permissions.IsAuthenticated(), IsLeadOwnerOrProductBusiness()]
        return [permissions.IsAuthenticated()]

    @action(
        detail=True,
        methods=["patch"],
        url_path="update-status",
        permission_classes=[permissions.IsAuthenticated, IsLeadOwnerOrProductBusiness],
    )
    def update_status(self, request, pk=None):
        """
        PATCH /api/v1/leads/leads/{id}/update-status/
        Faqat mahsulot egasi (business) status o'zgartira oladi.
        """
        lead = self.get_object()
        if request.user.role != "business" and not request.user.is_staff:
            return Response(
                {"detail": "Faqat biznes foydalanuvchi status o'zgartira oladi."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = LeadStatusSerializer(lead, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LeadSerializer(lead).data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    /api/v1/leads/orders/

    - User: o'z leadiga bog'liq orderni ko'radi.
    - Business: o'z mahsulotlariga bog'liq orderlarni ko'radi va yaratadi.
    - Kuryer: o'ziga tayinlangan orderlarni ko'radi.
    - Admin: barchasini boshqaradi.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related(
            "lead__user",
            "lead__product__business",
            "courier",
        )
        if user.is_staff or user.role == "admin":
            return qs.all()
        if user.role == "business":
            return qs.filter(lead__product__business=user)
        if user.role == "courier":
            return qs.filter(courier=user)
        # Oddiy foydalanuvchi — faqat o'z leadiga bog'liq orderlar
        return qs.filter(lead__user=user)

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrderParticipantOrAdmin()]
        return [permissions.IsAuthenticated()]
