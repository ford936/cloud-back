import os.path

from django.db import models
from django.contrib.auth.models import AbstractUser


def change_file_path(instance, filename):
    return os.path.join('cloud', instance.created_by.username, filename)


class User(AbstractUser):
    user_cloud_path = models.CharField(max_length=200, blank=True, null=True)


class File(models.Model):
    file = models.FileField(upload_to=change_file_path)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    size = models.FloatField()
    unload_date = models.DateTimeField(auto_now_add=True)
    last_load_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, models.CASCADE, related_name='files', blank=True, null=True)
    anonym_link = models.TextField(unique=True, blank=True, null=True)
