from rest_framework import serializers
from .models import Album
from accounts.serializers import UserSerializer


class AlbumSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    photo_count = serializers.ReadOnlyField()

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'description', 'cover_image', 'is_public',
            'owner', 'photo_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class AlbumCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'description', 'cover_image', 'is_public']


class PublicAlbumSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    photo_count = serializers.ReadOnlyField()

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'description', 'cover_image', 'is_public',
            'owner', 'photo_count', 'created_at', 'updated_at'
        ]
