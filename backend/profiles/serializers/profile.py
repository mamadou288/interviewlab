from rest_framework import serializers
from ..models import Profile
from .cvdocument import CVDocumentSerializer


class ProfileSerializer(serializers.ModelSerializer):
    cv_document = CVDocumentSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'cv_document', 'data_json', 
            'confirmed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['data_json', 'confirmed']

