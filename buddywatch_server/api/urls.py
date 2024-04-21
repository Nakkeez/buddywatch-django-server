from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CreateUserView, CustomTokenObtainPairView, ListVideoView, UploadVideoView, DeleteVideoView, \
    DownloadVideoView, PredictView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('videos/', ListVideoView.as_view(), name='videos'),
    path('videos/upload/', UploadVideoView.as_view(), name='upload-video'),
    path('videos/delete/<int:pk>/', DeleteVideoView.as_view(), name='delete-video'),
    path('videos/download/<int:pk>/', DownloadVideoView.as_view(), name='download-video'),
    path('predict/', PredictView.as_view(), name='predict')
]
