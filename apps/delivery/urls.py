from rest_framework.routers import DefaultRouter

from .views import DeliveryZoneViewSet

router = DefaultRouter()
router.register("zones", DeliveryZoneViewSet, basename="delivery-zone")

urlpatterns = router.urls
