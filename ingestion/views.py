import os
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from ingestion.serializers import EmailFileUploadSerializer
from ingestion.tasks import process_eml_file


class EmailFileUploadAPIView(APIView):
    """
    API endpoint to upload a .eml file and kick off asynchronous processing.
    Returns the Celery task ID for status tracking.
    """
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = EmailFileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        eml_file = serializer.validated_data['file']

        # Save uploaded file to media/uploads/
        upload_path = os.path.join('uploads', eml_file.name)
        full_path = default_storage.save(upload_path, eml_file)
        absolute_path = os.path.join(settings.MEDIA_ROOT, full_path)

        # Enqueue Celery task
        task = process_eml_file.apply_async(args=[absolute_path])

        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)