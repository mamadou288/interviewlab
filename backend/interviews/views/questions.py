from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAuthenticatedOwner
from ..models import InterviewSession
from ..serializers import InterviewQuestionSerializer


class InterviewQuestionsView(generics.ListAPIView):
    """Get all questions for an interview session."""
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewQuestionSerializer
    
    def get_queryset(self):
        session_id = self.kwargs['id']
        return InterviewSession.objects.get(id=session_id).questions.all()
    
    def list(self, request, *args, **kwargs):
        session_id = self.kwargs['id']
        
        # Check session exists and user owns it
        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if session.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        questions = session.questions.all()
        serializer = self.get_serializer(questions, many=True)
        
        return Response({
            'questions': serializer.data,
            'count': len(serializer.data)
        })

