from django.urls import path
from ingestion.views import EmailFileUploadAPIView

urlpatterns = [
    path('upload-eml/', EmailFileUploadAPIView.as_view(), name='audit-upload-eml'),
]
