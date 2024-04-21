from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from PIL import Image
import numpy as np

from .models import Video
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, VideoSerializer
from .utils import generate_and_save_thumbnail


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()  # Check that user doesn't already exist
    serializer_class = UserSerializer  # Validate creation data
    permission_classes = [AllowAny]  # Allow anyone to create user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ListVideoView(generics.ListAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Show user only their own videos
        return Video.objects.filter(owner=user)


class UploadVideoView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            video = serializer.save(owner=self.request.user)

            video_path = video.file.name
            # Generate and save the thumbnail
            generate_and_save_thumbnail(video_path, video)
            return JsonResponse({"success": True, "video": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return JsonResponse({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DeleteVideoView(generics.DestroyAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Let user delete only their only videos
        return Video.objects.filter(owner=user)


class DownloadVideoView(generics.RetrieveAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Let user download only their only videos
        return Video.objects.filter(owner=user)

    def get(self, request, *args, **kwargs):
        video = self.get_object()
        video_path = video.file.path
        with open(video_path, 'rb') as video_file:
            response = HttpResponse(video_file.read(), content_type='video/webm')
            response['Content-Disposition'] = f'attachment; filename={video.file.name}'
            # Let clients read filename from header
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            print(response['Content-Disposition'])
            return response


class PredictView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.FILES.get('image'):
            model = apps.get_app_config('api').model
            image_file = request.FILES['image']
            image = Image.open(image_file)
            image = image.convert('RGB')

            image = image.resize((120, 120))

            # Convert the image to a numpy array and normalize
            image_array = np.asarray(image) / 255.0

            # Expand dimensions to match the model's input shape
            image_array = np.expand_dims(image_array, axis=0)

            y_pred = model.predict(image_array)

            # Get bounding boxes and accuracy from the prediction and convert into serializable format
            prediction_result = {
                "bbox": y_pred[1][0].tolist(),
                "confidence": float(y_pred[0][0][0])
            }
            print(prediction_result)
            return JsonResponse({"success": True, "prediction": prediction_result}, status=status.HTTP_200_OK)

        return JsonResponse({"success": False, "error": "Request must have an image"},
                            status=status.HTTP_400_BAD_REQUEST)
