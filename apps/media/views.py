from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import MediaFile
from .permissions import IsUploaderOrAdmin
from .serializers import MediaFileSerializer, MediaUpdateSerializer, MediaUploadSerializer


@extend_schema(tags=["Media"], summary="Upload a file")
class MediaUploadView(generics.CreateAPIView):
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


@extend_schema(tags=["Media"])
class MediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsUploaderOrAdmin]

    def get_queryset(self):
        return MediaFile.objects.select_related("uploaded_by", "content_type")

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return MediaUpdateSerializer
        return MediaFileSerializer

    @extend_schema(summary="Retrieve a media file")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="Update a media file")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(summary="Delete a media file")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


@extend_schema(tags=["Media"], summary="List media files for an object")
class ObjectMediaListView(generics.ListAPIView):
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


@extend_schema(tags=["Media"], summary="List available content types for upload")
class ContentTypeListView(generics.GenericAPIView):
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
