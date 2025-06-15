from rest_framework import serializers


class EmailFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    