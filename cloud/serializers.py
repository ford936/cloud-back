from rest_framework import serializers
from cloud.models import User, File


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'password', 'is_staff', 'user_path']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'name', 'description', 'size', 'unload_date', 'last_load_date', 'created_by']