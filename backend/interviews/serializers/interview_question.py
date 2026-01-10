from rest_framework import serializers
from ..models import InterviewQuestion


class InterviewQuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'session', 'order', 'question_text', 'category',
            'difficulty', 'skill_tags_json', 'is_followup',
            'parent_question', 'created_at', 'answer'
        ]
        read_only_fields = ['id', 'session', 'created_at']
    
    def get_answer(self, obj):
        """Include answer data if it exists."""
        if hasattr(obj, 'answer'):
            # Import here to avoid circular import
            from .interview_answer import InterviewAnswerResponseSerializer
            return InterviewAnswerResponseSerializer(obj.answer).data
        return None

