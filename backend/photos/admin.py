from django.contrib import admin
from .models import Photo, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'album', 'owner', 'title', 'exif_camera_model', 'created_at']
    search_fields = ['title', 'description', 'album__title', 'owner__username', 'exif_camera_model']
    list_filter = ['created_at', 'exif_datetime_original']
    raw_id_fields = ['album', 'owner', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'image_width', 'image_height']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('album', 'owner', 'title', 'description', 'tags'),
        }),
        ('Images', {
            'fields': ('original_image', 'thumbnail_small', 'thumbnail_medium', 'thumbnail_large'),
        }),
        ('EXIF - Camera', {
            'fields': ('exif_camera_make', 'exif_camera_model', 'exif_lens_model', 
                       'exif_focal_length', 'exif_aperture', 'exif_shutter_speed',
                       'exif_iso', 'exif_flash', 'exif_white_balance'),
            'classes': ('collapse',),
        }),
        ('EXIF - Location & Time', {
            'fields': ('exif_datetime_original', 'exif_gps_latitude', 
                       'exif_gps_longitude', 'exif_gps_altitude'),
            'classes': ('collapse',),
        }),
        ('Technical', {
            'fields': ('file_size', 'image_width', 'image_height'),
            'classes': ('collapse',),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
