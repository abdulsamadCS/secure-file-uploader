import json
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from unittest.mock import patch, MagicMock
import boto3
from moto import mock_aws
from .models import EncryptedFile
from .storage import S3Storage, LocalStorage


@mock_aws
class FileUploadTestCase(TestCase):
    def setUp(self):
        self.url = reverse("upload_file")
        self.sample_file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
        settings.USE_S3 = True
        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"
        settings.AWS_S3_REGION_NAME = "us-east-1"

    def test_file_upload_s3_with_moto(self):
        # Create a mock S3 bucket
        s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)
        s3.create_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)

        response = self.client.post(self.url, {"file": self.sample_file})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("file_url", response_data)
        self.assertIn("file_id", response_data)
        self.assertIn("encryption_key", response_data)

        # Verify the file was "uploaded" to our mock S3
        s3_objects = s3.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        self.assertEqual(len(s3_objects.get("Contents", [])), 1)

        self.assertTrue(EncryptedFile.objects.filter(file_name="test_file.txt").exists())

    def test_file_upload_s3_error_with_moto(self):
        # Don't create a bucket, which will cause an error
        response = self.client.post(self.url, {"file": self.sample_file})

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertIn("S3 upload failed", response_data["error"])

    def test_file_upload_no_file(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
        self.assertEqual(response_data["error"], "No file provided")

    @patch("file_handler.views.StorageFactory.get_storage")
    def test_file_upload_local_storage(self, mock_get_storage):
        mock_storage = MagicMock(spec=LocalStorage)
        mock_storage.save_file.return_value = "/media/test_file.txt"
        mock_get_storage.return_value = mock_storage

        response = self.client.post(self.url, {"file": self.sample_file})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("file_url", response_data)
        self.assertIn("file_id", response_data)
        self.assertIn("encryption_key", response_data)
        self.assertTrue(EncryptedFile.objects.filter(file_name="test_file.txt").exists())

    @patch("file_handler.views.StorageFactory.get_storage")
    def test_file_upload_storage_error(self, mock_get_storage):
        mock_storage = MagicMock(spec=S3Storage)
        mock_storage.save_file.side_effect = Exception("Storage error")
        mock_get_storage.return_value = mock_storage

        response = self.client.post(self.url, {"file": self.sample_file})

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)

    @patch("file_handler.views.StorageFactory.get_storage")
    def test_large_file_upload(self, mock_get_storage):
        large_file_content = b"x" * 1024 * 1024 * 5  # 5 MB file
        large_file = SimpleUploadedFile("large_file.txt", large_file_content, content_type="text/plain")

        mock_storage = MagicMock(spec=S3Storage)
        mock_storage.save_file.return_value = "https://test-bucket.s3.amazonaws.com/large_file.txt"
        mock_get_storage.return_value = mock_storage

        response = self.client.post(self.url, {"file": large_file})

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("file_url", response_data)
        self.assertIn("file_id", response_data)
        self.assertIn("encryption_key", response_data)

    @patch("file_handler.encryption.encrypt_file")
    def test_encryption_error(self, mock_encrypt):
        mock_encrypt.side_effect = Exception("Encryption error")

        response = self.client.post(self.url, {"file": self.sample_file})

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
