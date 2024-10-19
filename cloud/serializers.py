from rest_framework import serializers

from cloud.models import User, File
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff

        return token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    user_cloud_path = serializers.CharField(max_length=200, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'password', 'email', 'is_staff', 'user_cloud_path']


class FileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, read_only=True)
    size = serializers.FloatField(read_only=True)
    last_load_date = serializers.DateTimeField(read_only=True)
    created_by = UserSerializer(read_only=True)
    anonym_link = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'file', 'name', 'description', 'size', 'unload_date', 'last_load_date', 'created_by',
                  'anonym_link']


class FileRetrieveSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    size = serializers.FloatField(read_only=True)
    last_load_date = serializers.DateTimeField(read_only=True)
    created_by = UserSerializer(read_only=True)
    file = serializers.FileField(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'file', 'name', 'description', 'size', 'unload_date', 'last_load_date', 'created_by',
                  'anonym_link']
