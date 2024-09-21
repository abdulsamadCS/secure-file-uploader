from django.contrib import admin
from django.urls import path
from file_handler.views import upload_encrypted_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', upload_encrypted_file, name='upload_file'),
]