from rest_framework import serializers
from .models import *

class FileListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFiles
        fields = ('id', 'file')