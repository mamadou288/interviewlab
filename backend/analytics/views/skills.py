from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import SkillStatsSerializer
from ..services.aggregator import get_skill_map_stats
from ..services.calculator import calculate_skill_mastery, calculate_skill_trend


class AnalyticsSkillsView(generics.ListAPIView):
    """
    GET /api/analytics/skills
    Returns skill-level analytics for authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SkillStatsSerializer

    def get_queryset(self):
        """Return skill stats for the authenticated user."""
        user = self.request.user
        
        # Get skill map stats
        skill_map = get_skill_map_stats(user)
        skill_mastery = skill_map.get('skill_mastery', {})
        
        # Build skill stats list
        skills_data = []
        for skill_tag, data in skill_mastery.items():
            # Calculate rolling score (mastery)
            rolling_score = calculate_skill_mastery(user, skill_tag)
            
            # Determine trend
            trend = calculate_skill_trend(user, skill_tag)
            
            skills_data.append({
                'tag': skill_tag,
                'rolling_score': rolling_score,
                'attempts': data['attempts'],
                'last_practiced_at': data['last_practiced'],
                'trend': trend,
            })
        
        # Sort by rolling_score (descending)
        skills_data.sort(key=lambda x: x['rolling_score'], reverse=True)
        
        return skills_data

    def list(self, request, *args, **kwargs):
        """Override list to return serialized data."""
        skills_data = self.get_queryset()
        serializer = self.get_serializer(skills_data, many=True)
        return Response({'skills': serializer.data})

