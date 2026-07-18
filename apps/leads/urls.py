from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, OrderViewSet

router = DefaultRouter()
router.register("leads", LeadViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls
