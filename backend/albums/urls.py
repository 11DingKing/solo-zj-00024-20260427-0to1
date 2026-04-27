from django.urls import path
from .views import (
    AlbumListCreateView,
    AlbumRetrieveUpdateDestroyView,
    PublicAlbumListView,
    UserAlbumListView,
)

urlpatterns = [
    path('', AlbumListCreateView.as_view(), name='album-list-create'),
    path('public/', PublicAlbumListView.as_view(), name='public-album-list'),
    path('user/<str:username>/', UserAlbumListView.as_view(), name='user-album-list'),
    path('<int:pk>/', AlbumRetrieveUpdateDestroyView.as_view(), name='album-detail'),
]
