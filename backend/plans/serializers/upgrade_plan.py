from rest_framework import serializers
from ..models import UpgradePlan
from interviews.serializers import InterviewSessionSerializer


class UpgradePlanSerializer(serializers.ModelSerializer):
    session = InterviewSessionSerializer(read_only=True)
    strengths = serializers.SerializerMethodField()
    weaknesses = serializers.SerializerMethodField()
    learning_objectives = serializers.SerializerMethodField()
    daily_plans = serializers.SerializerMethodField()
    next_interview = serializers.SerializerMethodField()
    
    class Meta:
        model = UpgradePlan
        fields = [
            'id', 'session', 'duration_days', 'strengths', 'weaknesses',
            'learning_objectives', 'daily_plans', 'next_interview', 'created_at'
        ]
        read_only_fields = ['id', 'session', 'created_at']
    
    def get_strengths(self, obj):
        return obj.plan_json.get('strengths', [])
    
    def get_weaknesses(self, obj):
        return obj.plan_json.get('weaknesses', [])
    
    def get_learning_objectives(self, obj):
        return obj.plan_json.get('learning_objectives', [])
    
    def get_daily_plans(self, obj):
        return obj.plan_json.get('daily_plans', [])
    
    def get_next_interview(self, obj):
        return obj.plan_json.get('next_interview', {})

