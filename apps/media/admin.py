from django.contrib import admin
from django.utils.html import format_html

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "preview", "purpose", "original_filename",
        "size_kb_display", "dimensions", "is_primary", "uploaded_by", "created_at",
    )
    list_filter = ("purpose", "is_primary")
    search_fields = ("original_filename", "alt_text", "uploaded_by__username")
    readonly_fields = (
        "preview", "original_filename", "mime_type",
        "size_bytes", "width", "height", "uploaded_by", "created_at",
        "content_type", "object_id",
    )
    ordering = ("-created_at",)

    @admin.display(description="Ko'rinish")
    def preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-height:60px;max-width:100px;object-fit:cover;border-radius:4px;">',
                obj.file.url,
            )
        return "—"

    @admin.display(description="Hajm (KB)")
    def size_kb_display(self, obj):
        return f"{obj.size_kb} KB"

    @admin.display(description="O'lcham")
    def dimensions(self, obj):
        if obj.width and obj.height:
            return f"{obj.width}×{obj.height}"
        return "—"
