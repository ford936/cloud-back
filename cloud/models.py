from django.db import models
from django.contrib.auth.models import AbstractUser, User
PATH = ''


class User(AbstractUser):
    user_cloud_path = models.CharField(max_length=200, blank=True, null=True)


class File(models.Model):
    file = models.FileField(upload_to=f'static/{PATH}')
    name = models.CharField(max_length=100)
    description = models.TextField()
    size = models.FloatField()
    unload_date = models.DateTimeField(auto_now_add=True)
    last_load_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, models.CASCADE, related_name='files', blank=True, null=True)