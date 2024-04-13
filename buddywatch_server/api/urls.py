from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import CreateUserView, VideoUploadView, PredictView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    # path('predict/', predict, name='predict'),
    path('predict/', PredictView.as_view(), name='predict')
]
