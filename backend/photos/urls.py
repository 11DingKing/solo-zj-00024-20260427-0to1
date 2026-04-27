from django.urls import path
from .views import (
    PhotoListCreateView,
    PhotoRetrieveUpdateDestroyView,
    BatchMoveView,
    BatchDeleteView,
    BatchTagView,
    PhotoTimelineView,
    TagListView,
)

urlpatterns = [
    path('', PhotoListCreateView.as_view(), name='photo-list-create'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('batch/move/', BatchMoveView.as_view(), name='batch-move'),
    path('batch/delete/', BatchDeleteView.as_view(), name='batch-delete'),
    path('batch/tag/', BatchTagView.as_view(), name='batch-tag'),
    path('timeline/', PhotoTimelineView.as_view(), name='photo-timeline'),
    path('timeline/<str:username>/', PhotoTimelineView.as_view(), name='user-photo-timeline'),
    path('<int:pk>/', PhotoRetrieveUpdateDestroyView.as_view(), name='photo-detail'),
]
