from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.apps import apps
from django.core.files.storage import default_storage
from PIL import Image
import numpy as np

from .models import Video
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, VideoSerializer
from .utils import generate_and_save_thumbnail


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user and check the username is unique.

    Returns:
        JsonResponse: Success message if successful, error message if not.
    """
    # Check that user doesn't already exist
    queryset = User.objects.all()
    # Validate creation data
    serializer_class = UserSerializer
    # Allow anyone to create user
    permission_classes = [AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view that returns the username along
    with the access and refresh tokens.

    Returns:
        JsonResponse: Access and refresh tokens along with the username.
    """
    serializer_class = CustomTokenObtainPairSerializer


class ListVideoView(generics.ListAPIView):
    """
    Lists all videos uploaded by the user.

    Returns:
        Video: List of videos uploaded by the user.
    """
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Show user only their own videos
        return Video.objects.filter(owner=user)


class UploadVideoView(generics.CreateAPIView):
    """
    Uploads a video file to the server.
    Request must be multipart/form-data with the video file in the 'file' field
    and video title in the 'title' field.

    Returns:
        JsonResponse: Success message and video data if successful, error message if not.
    """
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid():
            video = serializer.save(owner=self.request.user)

            video_url = video.file.name
            # Generate and save the thumbnail
            generate_and_save_thumbnail(video_url, video)
            return JsonResponse({"success": True, "video": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return JsonResponse({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DeleteVideoView(generics.DestroyAPIView):
    """
    Delete video file from the server by id.

    Returns:
        JsonResponse: Success message if successful, error message if not.
    """
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Let user delete only their only videos
        return Video.objects.filter(owner=user)


class DownloadVideoView(generics.RetrieveAPIView):
    """
    Download video file from the server by id.

    Returns:
        HttpResponse: Video file as a response if successful
        JsonResponse: Error message if not.
    """
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Let user download only their only videos
        return Video.objects.filter(owner=user)

    def get(self, request, *args, **kwargs):
        video = self.get_object()

        # If file exists, open the Azure Blob Storage file and return it as a response
        if default_storage.exists(video.file.name):
            file = default_storage.open(video.file.name, 'rb')
            response = HttpResponse(file, content_type='video/webm', status=status.HTTP_200_OK)
            # Add filename to the response headers
            response['Content-Disposition'] = f"attachment; filename=\"{video.file.name.split('/')[-1]}\""
            # Let clients read filename from header
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'

            return response
        else:
            return JsonResponse({"success": False, "error": "File not found."}, status=status.HTTP_404_NOT_FOUND)


class PredictView(generics.CreateAPIView):
    """
    Predict the bounding box coordinates and confidence score of human face in an image.
    Request must be multipart/form-data with the image file in the 'image' field.

    Returns:
        JsonResponse: Bounding box coordinates and confidence score if successful, error message if not.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.FILES.get('image'):
            # Get the model from the app registry
            model = apps.get_app_config('api').model
            image_file = request.FILES['image']
            # Open the image file and convert to RGB format
            image = Image.open(image_file)
            image = image.convert('RGB')

            # Resize the image to 120x120 for faster processing
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
