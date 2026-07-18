from rest_framework.routers import DefaultRouter

from .views import LeadViewSet, OrderViewSet

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
