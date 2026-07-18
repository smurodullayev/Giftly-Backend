from rest_framework import permissions


class IsLeadOwnerOrProductBusiness(permissions.BasePermission):
    """
    Lead:
      - Yaratgan foydalanuvchi o'qiy va o'chira oladi.
      - Mahsulot egasi (business) o'qiy va status'ni yangilay oladi.
      - Admin hamma narsani qila oladi.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == "admin":
            return True
        # Lead yaratuvchisi
        if obj.user == user:
            return True
        # Mahsulot egasi faqat o'qiy va status o'zgartira oladi
        if obj.product.business == user:
            return request.method in (*permissions.SAFE_METHODS, "PATCH")
        return False


class IsOrderParticipantOrAdmin(permissions.BasePermission):
    """
    Order:
      - Lead yaratuvchisi o'qiy oladi.
      - Mahsulot egasi (business) o'qiy va order yarata oladi.
      - Tayinlangan kuryer o'qiy oladi.
      - Admin hamma narsani qila oladi.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.role == "admin":
            return True
        if obj.lead.user == user:
            return request.method in permissions.SAFE_METHODS
        if obj.lead.product.business == user:
            return True
        if obj.courier == user:
            return request.method in permissions.SAFE_METHODS
        return False
