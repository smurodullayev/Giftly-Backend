from rest_framework import permissions


class IsUploaderOrAdmin(permissions.BasePermission):
    """
    MediaFile ni faqat yuklagan kishi yoki admin o'chira / o'zgartira oladi.
    O'qish — barcha autentifikatsiya qilingan foydalanuvchilarga.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.role == "admin":
            return True
        return obj.uploaded_by == request.user
