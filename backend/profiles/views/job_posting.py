from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..services.job_posting_parser import parse_job_posting


class ParseJobPostingView(generics.CreateAPIView):
    """
    Parse a job posting and extract structured information.
    POST /api/job-posting/parse
    Body: { "text": "job posting text..." }
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Job posting text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            parsed_data = parse_job_posting(text)
            return Response(parsed_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error parsing job posting: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

