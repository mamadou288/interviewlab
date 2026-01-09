from rest_framework import serializers
from ..models import InterviewSession
from roles.serializers import RoleCatalogSerializer


class InterviewSessionSerializer(serializers.ModelSerializer):
    role_selected = RoleCatalogSerializer(read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'user', 'profile', 'role_selected', 'role_source',
            'level', 'type', 'status', 'overall_score',
            'started_at', 'ended_at', 'created_at', 'updated_at', 'progress'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_progress(self, obj):
        """Calculate interview progress."""
        total_questions = obj.questions.count()
        answered_questions = obj.questions.filter(answer__isnull=False).count()
        
        return {
            'current_question': answered_questions + 1 if answered_questions < total_questions else total_questions,
            'total_questions': total_questions,
            'answered': answered_questions,
        }

