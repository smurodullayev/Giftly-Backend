from rest_framework import permissions


class IsBusinessOwnerOrReadOnly(permissions.BasePermission):
    """
    - GET, HEAD, OPTIONS: barcha autentifikatsiya qilingan foydalanuvchilarga.
    - POST: faqat role='business' foydalanuvchilarga.
    - PUT/PATCH/DELETE: faqat mahsulot egasiga (obj.business == request.user).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "business"
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.role == "admin":
            return True
        return obj.business == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Category va Occasion: o'qish hamma uchun,
    yozish faqat admin uchun.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "admin")
        )
