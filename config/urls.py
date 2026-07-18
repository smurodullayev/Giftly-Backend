from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

v1_patterns = [
    # Auth — JWT tokenlar
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # App endpointlari
    path("users/", include("apps.users.urls")),
    path("media/", include("apps.media.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("leads/", include("apps.leads.urls")),
    path("reviews/", include("apps.reviews.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(v1_patterns)),
    # OpenAPI schema va UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Dev muhitda media fayllarni serve qilish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
