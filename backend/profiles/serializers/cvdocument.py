from rest_framework import serializers
from ..models import CVDocument


class CVDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CVDocument
        fields = [
            'id', 'user', 'file', 'status', 'file_size', 
            'mime_type', 'created_at', 'updated_at', 'processed_at', 'file_url'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at', 'processed_at'
        ]
    
    def get_file_url(self, obj):
        """Return file URL if status is completed."""
        if obj.status == 'completed' and obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

