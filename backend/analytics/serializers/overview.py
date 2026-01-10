from rest_framework import serializers


class OverviewStatsSerializer(serializers.Serializer):
    """Serializer for analytics overview dashboard data."""
    overall_score = serializers.FloatField()
    total_sessions = serializers.IntegerField()
    score_trend = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    category_trend = serializers.DictField(
        child=serializers.FloatField()
    )
    top_improving_skills = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    top_weak_skills = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

