from rest_framework import serializers
from ..models import RoleCatalog


class RoleCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleCatalog
        fields = [
            'id', 'name', 'category', 'keywords_json', 
            'description', 'level_keywords_json', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

