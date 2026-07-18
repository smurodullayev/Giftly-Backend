from django.contrib.contenttypes.models import ContentType
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import MediaFile
from .permissions import IsUploaderOrAdmin
from .serializers import MediaFileSerializer, MediaUpdateSerializer, MediaUploadSerializer


class MediaUploadView(generics.CreateAPIView):
    """
    POST /api/v1/media/upload/
    multipart/form-data formatida fayl yuklash.

    Misol (product rasmi):
      file=<rasm>
      purpose=product_image
      content_type_id=<Product ContentType ID>
      object_id=<product.pk>
      is_primary=true
      alt_text=Gul guldasta

    Avatar yuklash:
      file=<rasm>
      purpose=user_avatar
      content_type_id=<User ContentType ID>
      object_id=<user.pk>
      is_primary=true
    """

    serializer_class = MediaUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.save()
        return Response(
            MediaFileSerializer(media, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/media/<id>/  — fayl ma'lumotlari
    PATCH  /api/v1/media/<id>/  — alt_text, is_primary, order yangilash
    DELETE /api/v1/media/<id>/  — faylni o'chirish (faylni diskdan ham o'chiradi)
    """

    permission_classes = [permissions.IsAuthenticated, IsUploaderOrAdmin]

    def get_queryset(self):
        return MediaFile.objects.select_related("uploaded_by", "content_type")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return MediaUpdateSerializer
        return MediaFileSerializer

    def perform_destroy(self, instance):
        # Faylni diskdan o'chirish
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


class ObjectMediaListView(generics.ListAPIView):
    """
    GET /api/v1/media/for/<content_type_id>/<object_id>/
    Berilgan obyektning barcha media fayllarini ro'yxatlash.

    Misol: /api/v1/media/for/12/5/  → Product #5 ning barcha rasmlari
    """

    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ct_id = self.kwargs["content_type_id"]
        obj_id = self.kwargs["object_id"]
        return (
            MediaFile.objects
            .filter(content_type_id=ct_id, object_id=obj_id)
            .select_related("uploaded_by")
        )


class ContentTypeListView(generics.GenericAPIView):
    """
    GET /api/v1/media/content-types/
    Frontend uchun content_type_id larini qaytaradi.

    Faqat media yuklash uchun kerakli modellar ko'rsatiladi.
    """

    permission_classes = [permissions.IsAuthenticated]

    ALLOWED_MODELS = {
        ("users", "user"),
        ("users", "businessprofile"),
        ("catalog", "product"),
    }

    def get(self, request, *args, **kwargs):
        result = []
        for app_label, model in self.ALLOWED_MODELS:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                result.append({
                    "id": ct.pk,
                    "app_label": app_label,
                    "model": model,
                })
            except ContentType.DoesNotExist:
                pass
        return Response(sorted(result, key=lambda x: x["model"]))
