from django.contrib import admin
from .models import Album


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'photo_count', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    list_filter = ['is_public', 'created_at']
    raw_id_fields = ['owner']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'cover_image'),
        }),
        ('Settings', {
            'fields': ('is_public', 'owner'),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
