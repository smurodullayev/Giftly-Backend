from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class CanWriteReview(BasePermission):
    """
    Sharh yozish uchun:
    - Autentifikatsiya bo'lgan bo'lishi shart.
    - 'delivered' statusli buyurtmasi bo'lishi shart.
    - Avval shu mahsulotga sharh yozmagan bo'lishi shart (model UniqueConstraint bilan kafolatlanadi).
    """

    message = "Sharh yozish uchun mahsulotni sotib olib, yetkazib olgan bo'lishingiz kerak."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        # POST (yangi sharh) — buyurtma tekshiruvi view da bajariladi
        return True


class IsReviewAuthorOrAdmin(BasePermission):
    """Sharhni faqat egasi yoki admin o'zgartira / o'chira oladi."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.role == "admin":
            return True
        return obj.user == request.user


class IsProductBusinessOwner(BasePermission):
    """Mahsulot egasi (business) faqat o'z mahsulotiga javob qoldira oladi."""

    message = "Faqat mahsulot egasi javob qoldira oladi."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.product.business == request.user
