from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.apps import apps
from PIL import Image
import numpy as np
from .serializers import UserSerializer
from .serializers import VideoSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()  # Check that user doesn't already exist
    serializer_class = UserSerializer  # Validate creation data
    permission_classes = [AllowAny]  # Allow anyone to create user


class VideoUploadView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]  # For development only

    def post(self, request, *args, **kwargs):
        video_serializer = VideoSerializer(data=request.data)
        if video_serializer.is_valid():
            video_serializer.save()
            return JsonResponse(video_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(video_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PredictView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # For development only

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
            return JsonResponse({"prediction": prediction_result}, status=status.HTTP_200_OK)

        return JsonResponse({"error": "Request must be POST with an image."}, status=status.HTTP_400_BAD_REQUEST)
