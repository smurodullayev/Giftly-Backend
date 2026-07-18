from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, OccasionViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("occasions", OccasionViewSet)
router.register("products", ProductViewSet)

urlpatterns = router.urls
