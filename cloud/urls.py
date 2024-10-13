from rest_framework import routers
from cloud.views import FileViewSet, UserViewSet
from django.urls import path, include

router = routers.SimpleRouter()

router.register(r'file', FileViewSet)
router.register('user', UserViewSet)
urlpatterns = [
    path('', include(router.urls)),
  ] + router.urls