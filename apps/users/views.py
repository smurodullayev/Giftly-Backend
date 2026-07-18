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


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/users/register/ — yangi foydalanuvchi."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """
    /api/v1/users/users/
    - Admin: barcha foydalanuvchilarni ko'radi va o'zgartiradi.
    - Oddiy user: faqat o'zini ko'radi.
    - DELETE o'rniga PATCH is_active=False — hisobni o'chirish emas, o'chirish.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
    http_method_names = ["get", "patch", "head", "options"]  # DELETE yo'q

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == "admin":
            return User.objects.all().order_by("-date_joined")
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """GET /api/v1/users/users/me/ — joriy foydalanuvchi profili."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="change-password",
        permission_classes=[permissions.IsAuthenticated],
    )
    def change_password(self, request):
        """POST /api/v1/users/users/change-password/"""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Parol muvaffaqiyatli o'zgartirildi."},
            status=status.HTTP_200_OK,
        )


class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    /api/v1/users/business-profiles/
    - Business user: faqat o'z profilini ko'radi/yaratadi/o'zgartiradi.
    - Admin: barchasini ko'radi.
    """

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


class CourierProfileViewSet(viewsets.ModelViewSet):
    """
    /api/v1/users/courier-profiles/
    - Kuryer user: faqat o'z profilini ko'radi/yaratadi/o'zgartiradi.
    - Admin: barchasini ko'radi.
    """

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
