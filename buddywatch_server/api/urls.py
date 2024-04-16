from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import CreateUserView, ListVideoView, UploadVideoView, DeleteVideoView, PredictView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('videos/', ListVideoView.as_view(), name='videos'),
    path('videos/upload/', UploadVideoView.as_view(), name='upload-video'),
    path('videos/delete/<int:pk>/', DeleteVideoView.as_view(), name='delete-video'),
    path('predict/', PredictView.as_view(), name='predict')
]
