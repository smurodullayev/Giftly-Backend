from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessProfileViewSet,
    CourierProfileViewSet,
    RegisterView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("business-profiles", BusinessProfileViewSet, basename="business-profile")
router.register("courier-profiles", CourierProfileViewSet, basename="courier-profile")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    *router.urls,
]
