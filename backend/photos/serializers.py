from rest_framework import serializers
from .models import Photo, Tag
from albums.serializers import AlbumSerializer
from accounts.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PhotoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    album = AlbumSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    has_gps = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = [
            'id', 'album', 'owner', 'title', 'description',
            'original_image', 'thumbnail_small', 'thumbnail_medium', 'thumbnail_large',
            'tags', 'has_gps',
            'exif_camera_make', 'exif_camera_model', 'exif_lens_model',
            'exif_focal_length', 'exif_aperture', 'exif_shutter_speed',
            'exif_iso', 'exif_flash', 'exif_white_balance',
            'exif_datetime_original', 'exif_gps_latitude', 'exif_gps_longitude', 'exif_gps_altitude',
            'file_size', 'image_width', 'image_height',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['album', 'original_image', 'title', 'description']


class PhotoUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Photo
        fields = ['title', 'description', 'tags']

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags_data is not None:
            tags = []
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
                tags.append(tag)
            instance.tags.set(tags)
        
        return instance


class PhotoListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    has_gps = serializers.ReadOnlyField()

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'description',
            'thumbnail_small', 'thumbnail_medium', 'thumbnail_large',
            'tags', 'has_gps', 'exif_datetime_original',
            'image_width', 'image_height', 'created_at'
        ]


class BatchPhotoSerializer(serializers.Serializer):
    photo_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )


class BatchMoveSerializer(BatchPhotoSerializer):
    target_album_id = serializers.IntegerField(required=True)


class BatchTagSerializer(BatchPhotoSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
