
from rest_framework import viewsets, status
from rest_framework.response import Response

from cloud.serializers import UserSerializer, FileSerializer

from .models import User, File
from transliterate import translit
from rest_framework.permissions import BasePermission, IsAuthenticated



class IsPostForCreateUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' or request.auth:
            return True
        else:
            return False


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsPostForCreateUser, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user_cloud_path'] = f'static/{serializer.validated_data["username"]}/'
        self.perform_create(serializer)
        user = User.objects.get(id=serializer.data['id'])
        user.set_password(user.password)
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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