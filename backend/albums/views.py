from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Album
from .serializers import (
    AlbumSerializer,
    AlbumCreateUpdateSerializer,
    PublicAlbumSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.owner == request.user
        return obj.owner == request.user


class AlbumPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class AlbumListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AlbumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Album.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlbumCreateUpdateSerializer
        return AlbumSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AlbumRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Album.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AlbumCreateUpdateSerializer
        return AlbumSerializer


class PublicAlbumListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicAlbumSerializer
    pagination_class = AlbumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'owner__username']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Album.objects.filter(is_public=True)


class UserAlbumListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AlbumSerializer
    pagination_class = AlbumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        username = self.kwargs.get('username')
        if self.request.user.is_authenticated and self.request.user.username == username:
            return Album.objects.filter(owner__username=username)
        return Album.objects.filter(owner__username=username, is_public=True)
