from django.db import models
from django.conf import settings
from albums.models import Album


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class Photo(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    original_image = models.ImageField(upload_to='photos/original/')
    thumbnail_small = models.ImageField(upload_to='photos/thumbs/small/', blank=True, null=True)
    thumbnail_medium = models.ImageField(upload_to='photos/thumbs/medium/', blank=True, null=True)
    thumbnail_large = models.ImageField(upload_to='photos/thumbs/large/', blank=True, null=True)
    
    tags = models.ManyToManyField(Tag, related_name='photos', blank=True)
    
    exif_camera_make = models.CharField(max_length=100, blank=True, null=True)
    exif_camera_model = models.CharField(max_length=100, blank=True, null=True)
    exif_lens_model = models.CharField(max_length=100, blank=True, null=True)
    exif_focal_length = models.CharField(max_length=50, blank=True, null=True)
    exif_aperture = models.CharField(max_length=50, blank=True, null=True)
    exif_shutter_speed = models.CharField(max_length=50, blank=True, null=True)
    exif_iso = models.IntegerField(blank=True, null=True)
    exif_flash = models.BooleanField(blank=True, null=True)
    exif_white_balance = models.CharField(max_length=50, blank=True, null=True)
    
    exif_datetime_original = models.DateTimeField(blank=True, null=True)
    exif_gps_latitude = models.FloatField(blank=True, null=True)
    exif_gps_longitude = models.FloatField(blank=True, null=True)
    exif_gps_altitude = models.FloatField(blank=True, null=True)
    
    file_size = models.IntegerField(default=0)
    image_width = models.IntegerField(blank=True, null=True)
    image_height = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photos'
        ordering = ['-exif_datetime_original', '-created_at']
        indexes = [
            models.Index(fields=['album', '-exif_datetime_original']),
            models.Index(fields=['owner', '-exif_datetime_original']),
            models.Index(fields=['-exif_datetime_original']),
        ]

    def __str__(self):
        return self.title or f"Photo {self.id}"

    @property
    def has_gps(self):
        return self.exif_gps_latitude is not None and self.exif_gps_longitude is not None
