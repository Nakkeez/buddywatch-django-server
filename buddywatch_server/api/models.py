from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
