from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BusinessProfileViewSet, CourierProfileViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("business-profiles", BusinessProfileViewSet)
router.register("courier-profiles", CourierProfileViewSet)

urlpatterns = router.urls
