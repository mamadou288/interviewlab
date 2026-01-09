from rest_framework import serializers
from ..models import InterviewQuestion


class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'session', 'order', 'question_text', 'category',
            'difficulty', 'skill_tags_json', 'is_followup',
            'parent_question', 'created_at'
        ]
        read_only_fields = ['id', 'session', 'created_at']

