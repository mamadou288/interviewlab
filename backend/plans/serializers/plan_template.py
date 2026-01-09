from rest_framework import serializers
from ..models import PlanTemplate


class PlanTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanTemplate
        fields = [
            'id', 'skill_tag', 'title', 'description',
            'steps_json', 'difficulty', 'duration_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

