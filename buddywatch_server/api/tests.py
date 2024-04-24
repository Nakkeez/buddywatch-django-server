from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.utils import json
from django.conf import settings
import os


class JWTClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    def authenticate(self, username=None, password=None):
        response = self.post('/api/token/', {'username': username, 'password': password})
        if response.status_code == 200:
            self.token = json.loads(response.content.decode('utf-8'))["access"]

    def _base_environ(self, **request):
        environ = super()._base_environ(**request)
        if self.token:
            environ['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        return environ


class ApiTest(TestCase):
    def setUp(self):
        self.client = JWTClient()
        self.user = User.objects.create_user(username='testuser', password='testing')
        self.client.authenticate(username='testuser', password='testing')

    def test_refresh_token(self):
        response = self.client.post("/api/token/", data={'username': 'testuser', 'password': 'testing'})
        self.assertEqual(response.status_code, 200, 'The token should be successfully returned.')

        response_content = json.loads(response.content.decode('utf-8'))
        refresh_token = response_content['refresh']

        response = self.client.post('/api/token/refresh/', data={'refresh': refresh_token})
        self.assertEqual(response.status_code, 200, 'The new access token should be successfully returned')

    def test_predict_view(self):
        test_image = os.path.join(settings.MEDIA_ROOT, 'testing', 'test_image.png')

        with open(test_image, 'rb') as image_file:
            image = SimpleUploadedFile('test_image.jpg', image_file.read(), content_type='image/jpeg')
            response = self.client.post('/api/predict/', {'image': image})
        self.assertEqual(response.status_code, 200, 'Response should be successfully returned')

        response_content = json.loads(response.content.decode('utf-8'))
        bbox = response_content['prediction']['bbox']
        label = response_content['prediction']['confidence']

        self.assertEqual(len(bbox), 4, 'Bounding box should have 4 coordinates')
        self.assertTrue(label, 'Confidence should be returned')

    def test_get_videos(self):
        response = self.client.get('/api/videos/')
        self.assertEqual(response.status_code, 200)
