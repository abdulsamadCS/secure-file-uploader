import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save_file(self, filename, content):
        pass


class S3Storage(Storage):
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def save_file(self, filename, content):
        try:
            self.s3_client.put_object(Body=content, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=filename)
            return (
                f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"
            )
        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")


class LocalStorage(Storage):
    def save_file(self, filename, content):
        try:
            file_path = default_storage.save(filename, ContentFile(content))
            return default_storage.url(file_path)
        except Exception as e:
            raise Exception(f"Local storage failed: {str(e)}")


class StorageFactory:
    @staticmethod
    def get_storage():
        if settings.USE_S3:
            return S3Storage()
        return LocalStorage()
