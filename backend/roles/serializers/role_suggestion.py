from rest_framework import serializers
from ..models import RoleSuggestion
from .role_catalog import RoleCatalogSerializer


class RoleSuggestionSerializer(serializers.ModelSerializer):
    role = RoleCatalogSerializer(read_only=True)
    
    class Meta:
        model = RoleSuggestion
        fields = ['id', 'role', 'score', 'reasons_json', 'created_at']
        read_only_fields = ['id', 'created_at']

