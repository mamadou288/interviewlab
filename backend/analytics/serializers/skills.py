from rest_framework import serializers


class SkillStatsSerializer(serializers.Serializer):
    """Serializer for skill-level analytics."""
    tag = serializers.CharField()
    rolling_score = serializers.FloatField()
    attempts = serializers.IntegerField()
    last_practiced_at = serializers.DateTimeField()
    trend = serializers.CharField()

