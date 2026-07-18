from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Foydalanuvchi faqat o'z profilini ko'ra/o'zgartira oladi.
    Admin (is_staff yoki role='admin') barcha profillarga kirishga ruxsat.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == "admin":
            return True
        return obj == request.user


class IsAdminRole(permissions.BasePermission):
    """Faqat role='admin' yoki is_staff=True bo'lgan foydalanuvchilarga ruxsat."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "admin")
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Umumiy maqsadli: obj.user == request.user yoki admin.
    BusinessProfile / CourierProfile kabi modellarda ishlatiladi.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == "admin":
            return True
        return obj.user == request.user
