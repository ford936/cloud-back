from django.contrib import admin
from django.urls import path, include
from cloud.service import custom_serve
from cloud.urls import urlpatterns
from django.conf import settings
from django.views.static import serve
from django.urls import re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from cloud.views import get_or_create_anonym_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include(urlpatterns)),
    path('anonym_link/<id>', get_or_create_anonym_link)
] + [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', custom_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
