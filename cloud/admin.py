from django.contrib import admin
from .models import *


@admin.register(File)
class FilesAdmin(admin.ModelAdmin):
    fields = ()
    list_display = ['id', 'file', 'name', 'description', 'size', 'unload_date', 'last_load_date']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'first_name', 'email', 'password', 'is_staff', 'user_cloud_path')
    list_display = ['id', 'username', 'first_name', 'email', 'password', 'is_staff', 'user_cloud_path']

