from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CouponApplyView, CouponViewSet

router = DefaultRouter()
router.register("coupons", CouponViewSet, basename="coupon")

urlpatterns = router.urls + [
    path("apply/", CouponApplyView.as_view({"post": "create"}), name="coupon-apply"),
]
