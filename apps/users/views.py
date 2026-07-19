from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BusinessProfile, CourierProfile, User
from .permissions import IsAdminRole, IsOwnerOrAdmin, IsSelfOrAdmin
from .serializers import (
    BusinessProfileSerializer,
    ChangePasswordSerializer,
    CourierProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)


@extend_schema(tags=["Users"], summary="Register a new user")
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(tags=["Users"], summary="List users"),
    retrieve=extend_schema(tags=["Users"], summary="Retrieve a user"),
    partial_update=extend_schema(tags=["Users"], summary="Partially update a user"),
)
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "admin":
            return User.objects.all().order_by("-date_joined")
        return User.objects.filter(pk=user.pk)

    @extend_schema(tags=["Users"], summary="Get current user profile")
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(tags=["Users"], summary="Change password")
    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        permission_classes=[permissions.IsAuthenticated],
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Parol muvaffaqiyatli o'zgartirildi."},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(tags=["Users"], summary="List business profiles"),
    retrieve=extend_schema(tags=["Users"], summary="Retrieve a business profile"),
    create=extend_schema(tags=["Users"], summary="Create a business profile"),
    update=extend_schema(tags=["Users"], summary="Update a business profile"),
    partial_update=extend_schema(tags=["Users"], summary="Partially update a business profile"),
    destroy=extend_schema(tags=["Users"], summary="Delete a business profile"),
)
class BusinessProfileViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "admin":
            return BusinessProfile.objects.select_related("user").all()
        return BusinessProfile.objects.select_related("user").filter(user=user)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.BUSINESS:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Faqat 'business' rolidagi foydalanuvchi profil yarata oladi."
            )
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(tags=["Users"], summary="List courier profiles"),
    retrieve=extend_schema(tags=["Users"], summary="Retrieve a courier profile"),
    create=extend_schema(tags=["Users"], summary="Create a courier profile"),
    update=extend_schema(tags=["Users"], summary="Update a courier profile"),
    partial_update=extend_schema(tags=["Users"], summary="Partially update a courier profile"),
    destroy=extend_schema(tags=["Users"], summary="Delete a courier profile"),
)
class CourierProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CourierProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "admin":
            return CourierProfile.objects.select_related("user").all()
        return CourierProfile.objects.select_related("user").filter(user=user)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.COURIER:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "Faqat 'courier' rolidagi foydalanuvchi profil yarata oladi."
            )
        serializer.save(user=self.request.user)
