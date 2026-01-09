from rest_framework import serializers
from ..models import InterviewAnswer
from .interview_question import InterviewQuestionSerializer


class InterviewAnswerSerializer(serializers.Serializer):
    """Serializer for answer submission."""
    question_id = serializers.UUIDField()
    answer_text = serializers.CharField()
    time_seconds = serializers.IntegerField(min_value=0)


class InterviewAnswerResponseSerializer(serializers.ModelSerializer):
    """Serializer for answer response with scores and feedback."""
    question = InterviewQuestionSerializer(read_only=True)
    
    class Meta:
        model = InterviewAnswer
        fields = [
            'id', 'question', 'answer_text', 'scores_json',
            'feedback_json', 'skill_tags_json', 'submitted_at', 'time_seconds'
        ]
        read_only_fields = ['id', 'submitted_at']

