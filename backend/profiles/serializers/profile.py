from rest_framework import serializers
from ..models import Profile
from .cvdocument import CVDocumentSerializer


class ProfileSerializer(serializers.ModelSerializer):
    cv_document = CVDocumentSerializer(read_only=True)
    # Include user information
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'user_email', 'user_first_name', 'user_last_name', 
            'user_full_name', 'cv_document', 'data_json', 
            'confirmed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_user_full_name(self, obj):
        """Return full name or email if name not available."""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip()
        return obj.user.email


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['data_json', 'confirmed']
        read_only_fields = []

