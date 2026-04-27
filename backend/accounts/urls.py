from django.urls import path
from .views import (
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    PublicUserProfileView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/<str:username>/', PublicUserProfileView.as_view(), name='public-user-profile'),
]
