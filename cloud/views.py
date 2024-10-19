import os
from pathlib import Path

from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import hashlib

from cloud.serializers import UserSerializer, FileSerializer, FileRetrieveSerializer
from .models import User, File
from transliterate import translit
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsPostForCreateUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' or request.auth:
            return True
        else:
            return False


class IsUseAnonLInk(BasePermission):
    def has_permission(self, request, view):
        return True


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsPostForCreateUser, ]

    def create(self, request, *args, **kwargs):
        import re

        valid_email = re.search(r'^[\w\.-]+@[\w\.-]+\.\w+$', request.data['email'])
        valid_username = re.search(r'^[a-zA-Z][a-zA-Z0-9]{3,19}$', request.data['username'])
        valid_password = re.search(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{6,}$', request.data['password'])

        if valid_email and valid_username and valid_password:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['user_cloud_path'] = f'static/{serializer.validated_data["username"]}/'
            self.perform_create(serializer)
            user = User.objects.get(id=serializer.data['id'])
            user.set_password(user.password)
            user.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'error': 'not valid '}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()) if request.user.is_superuser else User.objects.filter(
            id=request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()) if request.user.is_superuser else File.objects.filter(
            created_by=request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = FileRetrieveSerializer
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        self.serializer_class = FileRetrieveSerializer
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.name != request.data['name']:
            old_path = instance.file.path
            instance.file.name = f"cloud/{instance.created_by.username}/{request.data['name']}"
            instance.save()
            new_path = instance.file.path
            os.rename(old_path, new_path)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['file'].name = translit(serializer.validated_data['file'].name,
                                                          language_code='ru', reversed=True)
        serializer.validated_data['name'] = serializer.validated_data['file'].name
        serializer.validated_data['size'] = serializer.validated_data['file'].size
        serializer.validated_data['created_by'] = request.user
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_or_create_anonym_link(request, id):
    try:
        file = File.objects.get(id=id)
        if not file.anonym_link:
            h = hashlib.md5(file.name.encode())
            p = h.hexdigest()
            file.anonym_link = p
            file.save()
        return Response({'link': file.anonym_link})
    except:
        return Response({'error': 'bad file id'}, status=status.HTTP_404_NOT_FOUND)
