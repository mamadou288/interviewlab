from rest_framework import serializers
import uuid
from interviews.serializers import InterviewSessionSerializer


class SessionHistorySerializer(serializers.Serializer):
    """Serializer for session history."""
    id = serializers.UUIDField()
    role_selected = serializers.DictField()
    type = serializers.CharField()
    level = serializers.CharField()
    overall_score = serializers.IntegerField(allow_null=True)
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField(allow_null=True)
    progress = serializers.DictField(allow_null=True)

