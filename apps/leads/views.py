from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Lead, Order
from .permissions import IsLeadOwnerOrProductBusiness, IsOrderParticipantOrAdmin
from .serializers import LeadSerializer, LeadStatusSerializer, OrderSerializer


@extend_schema_view(
    list=extend_schema(tags=["Leads"], summary="List leads"),
    retrieve=extend_schema(tags=["Leads"], summary="Retrieve a lead"),
    create=extend_schema(tags=["Leads"], summary="Create a lead"),
    update=extend_schema(tags=["Leads"], summary="Update a lead"),
    partial_update=extend_schema(tags=["Leads"], summary="Partially update a lead"),
    destroy=extend_schema(tags=["Leads"], summary="Delete a lead"),
)
class LeadViewSet(viewsets.ModelViewSet):
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
        return qs.filter(user=user)

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy", "update_status"):
            return [permissions.IsAuthenticated(), IsLeadOwnerOrProductBusiness()]
        return [permissions.IsAuthenticated()]

    @extend_schema(tags=["Leads"], summary="Update lead status")
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-status",
        permission_classes=[permissions.IsAuthenticated, IsLeadOwnerOrProductBusiness],
    )
    def update_status(self, request, pk=None):
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


@extend_schema_view(
    list=extend_schema(tags=["Orders"], summary="List orders"),
    retrieve=extend_schema(tags=["Orders"], summary="Retrieve an order"),
    create=extend_schema(tags=["Orders"], summary="Create an order"),
    update=extend_schema(tags=["Orders"], summary="Update an order"),
    partial_update=extend_schema(tags=["Orders"], summary="Partially update an order"),
    destroy=extend_schema(tags=["Orders"], summary="Delete an order"),
)
class OrderViewSet(viewsets.ModelViewSet):
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
        return qs.filter(lead__user=user)

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrderParticipantOrAdmin()]
        return [permissions.IsAuthenticated()]
