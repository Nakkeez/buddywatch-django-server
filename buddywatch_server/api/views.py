from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.apps import apps
from PIL import Image
import numpy as np


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


@csrf_exempt  # Disabled for development! Must be enabled!
def predict(request):
    if request.method == 'POST' and request.FILES.get('image'):
        model = apps.get_app_config('api').model
        image_file = request.FILES['image']
        print(image_file)
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
        return JsonResponse({"prediction": prediction_result})

    return JsonResponse({"error": "Request must be POST with an image."}, status=400)
