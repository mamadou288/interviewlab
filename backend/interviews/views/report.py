from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAuthenticatedOwner
from ..models import InterviewSession
from ..services.report import generate_report


class InterviewReportView(generics.RetrieveAPIView):
    """Get interview session report."""
    permission_classes = [IsAuthenticated, IsAuthenticatedOwner]
    queryset = InterviewSession.objects.all()
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        session = self.get_object()
        
        # Generate report
        report = generate_report(str(session.id))
        
        if not report:
            return Response(
                {'error': 'Could not generate report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(report)

