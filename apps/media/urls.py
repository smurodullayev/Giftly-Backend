from django.urls import path

from .views import ContentTypeListView, MediaDetailView, MediaUploadView, ObjectMediaListView

urlpatterns = [
    # Fayl yuklash
    path("upload/", MediaUploadView.as_view(), name="media-upload"),
    # Bitta fayl: ko'rish, yangilash, o'chirish
    path("<int:pk>/", MediaDetailView.as_view(), name="media-detail"),
    # Obyektga bog'liq barcha fayllar
    path(
        "for/<int:content_type_id>/<int:object_id>/",
        ObjectMediaListView.as_view(),
        name="media-for-object",
    ),
    # Frontend uchun content_type ID lari
    path("content-types/", ContentTypeListView.as_view(), name="media-content-types"),
]
