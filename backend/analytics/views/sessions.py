from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from interviews.models import InterviewSession
from ..serializers import SessionHistorySerializer


class AnalyticsSessionsView(generics.ListAPIView):
    """
    GET /api/analytics/sessions
    Returns paginated session history with filters.
    Query params: limit, offset, type (filter by interview type)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SessionHistorySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['started_at', 'ended_at', 'overall_score']
    ordering = ['-started_at']

    def get_queryset(self):
        """Return completed sessions for the authenticated user."""
        queryset = InterviewSession.objects.filter(
            user=self.request.user,
            status='completed'
        ).select_related('role_selected')
        
        # Manual filtering by type if provided
        interview_type = self.request.query_params.get('type', None)
        if interview_type:
            queryset = queryset.filter(type=interview_type)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to format response with count."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get limit from query params
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[:limit]
        
        # Use InterviewSessionSerializer for full data
        from interviews.serializers import InterviewSessionSerializer
        serializer = InterviewSessionSerializer(queryset, many=True)
        
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
        })

