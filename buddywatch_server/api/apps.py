from django.apps import AppConfig
from django.conf import settings
import tensorflow as tf
import os


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    model = None

    def ready(self):
        file_path = os.path.join(settings.BASE_DIR, 'buddywatch_face.h5')
        print('Loading model...')
        ApiConfig.model = tf.keras.models.load_model(file_path)
        print('Model loaded successfully')
