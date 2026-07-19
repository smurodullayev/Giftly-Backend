from drf_spectacular.utils import extend_schema
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


@extend_schema(tags=["Users"])
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "admin":
            return User.objects.all().order_by("-date_joined")
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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


@extend_schema(tags=["Users"])
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


@extend_schema(tags=["Users"])
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
