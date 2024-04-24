from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.utils import json
from django.conf import settings
import json
import os


class JWTClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    def authenticate(self, username=None, password=None):
        """
        Authenticate the test user and store the token.
        :param username: username of the test user
        :param password: password of the test user
        """
        response = self.post('/api/token/', {'username': username, 'password': password})
        if response.status_code == 200:
            self.token = json.loads(response.content.decode('utf-8'))["access"]

    def _base_environ(self, **request):
        """
        Add the Authorization header to the request.
        :param self: instance of the client
        :param request: request data
        """
        environ = super()._base_environ(**request)
        if self.token:
            environ['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        return environ


class ApiTest(TestCase):
    def setUp(self):
        """
        Set up the test client and test user.
        """
        self.client = JWTClient()
        self.user = User.objects.create_user(username='testuser', password='testing')
        self.client.authenticate(username='testuser', password='testing')

    def test_refresh_token(self):
        """
        Test the token and refresh token views.
        """
        response = self.client.post("/api/token/", data={'username': 'testuser', 'password': 'testing'})
        self.assertEqual(response.status_code, 200, 'The token should be successfully returned.')

        response_content = json.loads(response.content.decode('utf-8'))
        refresh_token = response_content['refresh']

        response = self.client.post('/api/token/refresh/', data={'refresh': refresh_token})
        self.assertEqual(response.status_code, 200, 'The new access token should be successfully returned')

    def test_predict_view(self):
        """
        Test the predict view with a test image.
        """
        test_image = os.path.join(settings.MEDIA_ROOT, 'testing', 'test_image.png')

        # Open image from media/testing folder and upload it to the predict view
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
        """
        Test list video view by getting all videos for test user.
        """
        response = self.client.get('/api/videos/')
        self.assertEqual(response.status_code, 200)

    def test_upload_video(self):
        """
        Test upload and delete video view by first uploading
        test video and deleting it afterward.
        """
        response_before = self.client.get('/api/videos/')
        videos_before = json.loads(response_before.content.decode('utf-8'))
        video_amount_before = len(videos_before)

        test_video = os.path.join(settings.MEDIA_ROOT, 'testing', 'test_video.webm')

        # Open video from media/testing folder and upload it to the upload view
        with open(test_video, 'rb') as video_file:
            video = SimpleUploadedFile('test_video.webm', video_file.read(), content_type='video/mp4')
            response_upload = self.client.post('/api/videos/upload/', {'file': video, 'title': 'Test video'})
        self.assertEqual(response_upload.status_code, 201, 'Video should be successfully uploaded')

        response_during = self.client.get('/api/videos/')
        videos_during = json.loads(response_during.content.decode('utf-8'))
        video_amount_during = len(videos_during)
        self.assertEqual(video_amount_during, video_amount_before + 1, 'Video amount should be increased by 1')

        video_id = videos_during[0]['id']
        response_delete = self.client.delete(f'/api/videos/delete/{video_id}/')
        self.assertEqual(response_delete.status_code, 204, 'Video should be successfully deleted')

        response_after = self.client.get('/api/videos/')
        videos_after = json.loads(response_after.content.decode('utf-8'))
        video_amount_after = len(videos_after)
        self.assertEqual(video_amount_after, video_amount_before, 'Video amount should be the same as before')
