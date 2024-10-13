from rest_framework import viewsets, status
from rest_framework.response import Response
from cloud.serializers import UserSerializer, FileSerializer
from .models import User, File
from transliterate import translit
# PATH = ''


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()) if request.user.is_superuser else File.objects.filter(created_by=request.user.id)
        # queryset = self.filter_queryset(self.get_queryset())
        que = File.objects.filter(created_by=request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['file'].name:
            serializer.validated_data['file'].name = translit(serializer.validated_data['file'].name,
                                                              language_code='ru', reversed=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)