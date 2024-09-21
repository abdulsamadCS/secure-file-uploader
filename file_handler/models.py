from django.db import models


class EncryptedFile(models.Model):
    file_id = models.CharField(max_length=255, unique=True)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
