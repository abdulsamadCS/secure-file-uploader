import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .storage import StorageFactory
from .encryption import encrypt_file
from .models import EncryptedFile


@csrf_exempt
@require_http_methods(["POST"])
def upload_encrypted_file(request):
    try:
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)

        uploaded_file = request.FILES["file"]
        file_content = uploaded_file.read()

        encrypted_content, encryption_key = encrypt_file(file_content)
        unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"

        storage = StorageFactory.get_storage()
        file_url = storage.save_file(unique_filename, encrypted_content)

        EncryptedFile.objects.create(file_id=unique_filename, file_name=uploaded_file.name, file_url=file_url)

        return JsonResponse(
            {
                "message": "File uploaded and encrypted successfully",
                "file_url": file_url,
                "file_id": unique_filename,
                "encryption_key": encryption_key,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
