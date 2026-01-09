from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAuthenticatedOwner
from ..models import InterviewSession, InterviewQuestion, InterviewAnswer
from ..serializers import InterviewAnswerSerializer, InterviewAnswerResponseSerializer
from ..services.scorer import score_answer, calculate_overall_score
from ..services.feedback import generate_feedback


class InterviewAnswerView(generics.CreateAPIView):
    """Submit an answer and get scores/feedback."""
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewAnswerSerializer
    
    def create(self, request, *args, **kwargs):
        session_id = self.kwargs['id']
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text')
        time_seconds = request.data.get('time_seconds', 0)
        
        # Validate required fields
        if not all([question_id, answer_text]):
            return Response(
                {'error': 'question_id and answer_text are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get session and verify ownership
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
        
        # Get question
        try:
            question = InterviewQuestion.objects.get(id=question_id, session=session)
        except InterviewQuestion.DoesNotExist:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if answer already exists
        if hasattr(question, 'answer'):
            return Response(
                {'error': 'Answer already submitted for this question'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Score the answer
        scores = score_answer(answer_text, question)
        
        # Generate feedback
        feedback = generate_feedback(answer_text, scores, question)
        
        # Get skill tags from question
        skill_tags = question.skill_tags_json or []
        
        # Create answer
        answer = InterviewAnswer.objects.create(
            question=question,
            answer_text=answer_text,
            time_seconds=time_seconds,
            scores_json=scores,
            feedback_json=feedback,
            skill_tags_json=skill_tags
        )
        
        # Serialize and return
        response_serializer = InterviewAnswerResponseSerializer(answer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

