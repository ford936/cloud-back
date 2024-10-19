import mimetypes
import posixpath
from pathlib import Path

from django.http import HttpResponse, Http404, HttpResponseNotModified, FileResponse
from django.utils._os import safe_join
from django.utils.http import http_date
from django.views.static import directory_index, was_modified_since
# from pkg_resources import _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response

from cloud.models import File
from cloud.views import IsUseAnonLInk


@api_view(['GET'])
@permission_classes([IsUseAnonLInk])
def custom_serve(request, path: str, document_root=None, show_indexes=False):
    if File.objects.filter(anonym_link=path.split('/')[1]).exists():
        file = File.objects.get(anonym_link=path.split('/')[1]) # 'cloud/admin/Zlobin_Maksim.pdf'
        i = file
        path = file.file.name
    # elif request.user.is_anonymous:
    #     return HttpResponse({'error: 403'}, status=status.HTTP_403_FORBIDDEN)
    user = path.split('/')[1]
    # if user != request.user.username:
    #     return HttpResponse({'error: 403'}, status=status.HTTP_403_FORBIDDEN)
    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        if show_indexes:
            return directory_index(path, fullpath)
        raise Response({'error': 'not valid '}, status=status.HTTP_404_NOT_FOUND)
    if not fullpath.exists():
        raise Response({'error': 'not valid '}, status=status.HTTP_404_NOT_FOUND)
    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not was_modified_since(
            request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime
    ):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(fullpath.open("rb"), content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response
