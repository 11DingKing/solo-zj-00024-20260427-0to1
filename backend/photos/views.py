from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from collections import defaultdict

from .models import Photo, Tag
from .serializers import (
    PhotoSerializer,
    PhotoCreateSerializer,
    PhotoUpdateSerializer,
    PhotoListSerializer,
    BatchMoveSerializer,
    BatchTagSerializer,
    BatchPhotoSerializer,
    TagSerializer,
)
from .utils import (
    generate_thumbnails,
    extract_exif_data,
    validate_file_size,
)
from albums.models import Album


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.album.is_public or obj.owner == request.user
        return obj.owner == request.user


class PhotoPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class PhotoListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = PhotoPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags__name']
    ordering_fields = ['created_at', 'exif_datetime_original', 'image_width']
    ordering = ['-exif_datetime_original', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PhotoCreateSerializer
        return PhotoListSerializer

    def get_queryset(self):
        user = self.request.user
        album_id = self.request.query_params.get('album_id')
        tag = self.request.query_params.get('tag')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        queryset = Photo.objects.filter(owner=user)
        
        if album_id:
            queryset = queryset.filter(album_id=album_id)
        
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(exif_datetime_original__gte=date_from_dt)
            except:
                pass
        
        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(exif_datetime_original__lte=date_to_dt)
            except:
                pass
        
        return queryset.distinct()

    def perform_create(self, serializer):
        album_id = self.request.data.get('album')
        album = Album.objects.get(id=album_id, owner=self.request.user)
        
        image_file = self.request.FILES.get('original_image')
        
        try:
            file_size = validate_file_size(image_file)
        except ValueError as e:
            raise serializers.ValidationError({'original_image': str(e)})
        
        exif_data = extract_exif_data(image_file)
        
        photo = serializer.save(
            owner=self.request.user,
            album=album,
            file_size=file_size,
            **exif_data
        )
        
        image_file.seek(0)
        generate_thumbnails(image_file, photo)
        photo.save()


class PhotoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Photo.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PhotoUpdateSerializer
        return PhotoSerializer


class BatchMoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BatchMoveSerializer

    def post(self, request):
        serializer = BatchMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo_ids = serializer.validated_data['photo_ids']
        target_album_id = serializer.validated_data['target_album_id']
        
        try:
            target_album = Album.objects.get(id=target_album_id, owner=request.user)
        except Album.DoesNotExist:
            return Response(
                {'error': 'Target album not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        photos = Photo.objects.filter(id__in=photo_ids, owner=request.user)
        moved_count = photos.update(album=target_album)
        
        return Response({
            'message': f'Successfully moved {moved_count} photos',
            'moved_count': moved_count
        }, status=status.HTTP_200_OK)


class BatchDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BatchPhotoSerializer

    def post(self, request):
        serializer = BatchPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo_ids = serializer.validated_data['photo_ids']
        photos = Photo.objects.filter(id__in=photo_ids, owner=request.user)
        
        deleted_count = 0
        for photo in photos:
            if photo.original_image:
                photo.original_image.delete(save=False)
            if photo.thumbnail_small:
                photo.thumbnail_small.delete(save=False)
            if photo.thumbnail_medium:
                photo.thumbnail_medium.delete(save=False)
            if photo.thumbnail_large:
                photo.thumbnail_large.delete(save=False)
            deleted_count += 1
            photo.delete()
        
        return Response({
            'message': f'Successfully deleted {deleted_count} photos',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)


class BatchTagView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BatchTagSerializer

    def post(self, request):
        serializer = BatchTagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo_ids = serializer.validated_data['photo_ids']
        tag_names = serializer.validated_data['tags']
        
        tags = []
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
            tags.append(tag)
        
        photos = Photo.objects.filter(id__in=photo_ids, owner=request.user)
        
        for photo in photos:
            photo.tags.add(*tags)
        
        return Response({
            'message': f'Successfully tagged {photos.count()} photos',
            'tagged_count': photos.count()
        }, status=status.HTTP_200_OK)


class PhotoTimelineView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = PhotoPagination

    def get(self, request, username=None):
        if username:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if request.user.is_authenticated and request.user == user:
                    photos = Photo.objects.filter(owner=user)
                else:
                    photos = Photo.objects.filter(owner=user, album__is_public=True)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            photos = Photo.objects.filter(owner=request.user)
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                photos = photos.filter(exif_datetime_original__gte=date_from_dt)
            except:
                pass
        
        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                photos = photos.filter(exif_datetime_original__lte=date_to_dt)
            except:
                pass
        
        photos = photos.order_by('-exif_datetime_original', '-created_at')
        
        paginator = PhotoPagination()
        page = paginator.paginate_queryset(photos, request, view=self)
        
        grouped = defaultdict(list)
        
        for photo in page:
            date_key = None
            if photo.exif_datetime_original:
                date_key = photo.exif_datetime_original.strftime('%Y-%m')
            else:
                date_key = photo.created_at.strftime('%Y-%m')
            
            photo_serializer = PhotoListSerializer(photo, context={'request': request})
            grouped[date_key].append(photo_serializer.data)
        
        timeline = []
        for month in sorted(grouped.keys(), reverse=True):
            year, mon = month.split('-')
            timeline.append({
                'month': month,
                'year': int(year),
                'month_name': datetime(int(year), int(mon), 1).strftime('%B %Y'),
                'photos': grouped[month],
                'photo_count': len(grouped[month])
            })
        
        return paginator.get_paginated_response({
            'timeline': timeline,
            'total_months': len(timeline)
        })


class TagListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(photos__owner=self.request.user).distinct().order_by('name')
