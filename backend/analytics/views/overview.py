from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import OverviewStatsSerializer
from ..services.aggregator import get_session_stats, get_progress_stats
from ..services.calculator import (
    calculate_score_trend,
    calculate_category_trend,
    get_top_improving_skills,
    get_top_weak_skills,
)


class AnalyticsOverviewView(generics.RetrieveAPIView):
    """
    GET /api/analytics/overview
    Returns dashboard overview stats for authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OverviewStatsSerializer

    def get_object(self):
        """Return overview stats for the authenticated user."""
        user = self.request.user
        
        # Get session stats
        session_stats = get_session_stats(user)
        
        # Get progress stats (sessions for trend calculation)
        progress_stats = get_progress_stats(user)
        sessions = progress_stats.get('sessions', [])
        
        # Calculate trends
        score_trend = calculate_score_trend(sessions)
        category_trend = calculate_category_trend(sessions)
        
        # Get top skills
        top_improving = get_top_improving_skills(user, limit=5)
        top_weak = get_top_weak_skills(user, limit=5)
        
        # Build overview data
        overview_data = {
            'overall_score': session_stats.get('average_score', 0.0),
            'total_sessions': session_stats.get('total_sessions', 0),
            'score_trend': score_trend,
            'category_trend': category_trend,
            'top_improving_skills': top_improving,
            'top_weak_skills': top_weak,
        }
        
        return overview_data

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return serialized data."""
        overview_data = self.get_object()
        serializer = self.get_serializer(overview_data)
        return Response(serializer.data)

