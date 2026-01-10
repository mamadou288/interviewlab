from rest_framework import serializers
from ..models import InterviewAnswer


class InterviewAnswerSerializer(serializers.Serializer):
    """Serializer for answer submission."""
    question_id = serializers.UUIDField()
    answer_text = serializers.CharField()
    time_seconds = serializers.IntegerField(min_value=0)


class InterviewAnswerResponseSerializer(serializers.ModelSerializer):
    """Serializer for answer response with scores and feedback."""
    question = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewAnswer
        fields = [
            'id', 'question', 'answer_text', 'scores_json',
            'feedback_json', 'skill_tags_json', 'submitted_at', 'time_seconds'
        ]
        read_only_fields = ['id', 'submitted_at']
    
    def get_question(self, obj):
        """Include question data without circular import."""
        # Import here to avoid circular import
        from .interview_question import InterviewQuestionSerializer
        # Create a serializer without the answer field to avoid recursion
        question_data = {
            'id': obj.question.id,
            'order': obj.question.order,
            'question_text': obj.question.question_text,
            'category': obj.question.category,
            'difficulty': obj.question.difficulty,
            'skill_tags_json': obj.question.skill_tags_json,
            'is_followup': obj.question.is_followup,
            'created_at': obj.question.created_at,
        }
        return question_data

