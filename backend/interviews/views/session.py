from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.permissions import IsAuthenticatedOwner
from roles.models import RoleCatalog
from profiles.models import Profile
from ..models import InterviewSession
from ..serializers import InterviewSessionSerializer
from ..services.generator import generate_interview_questions


class InterviewSessionCreateView(generics.CreateAPIView):
    """Create a new interview session and generate questions."""
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewSessionSerializer
    
    def create(self, request, *args, **kwargs):
        role_id = request.data.get('role_id')
        level = request.data.get('level')
        interview_type = request.data.get('type')
        profile_id = request.data.get('profile_id')
        role_source = request.data.get('role_source', 'catalog')
        
        # Validate required fields
        if not all([role_id, level, interview_type]):
            return Response(
                {'error': 'role_id, level, and type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate choices
        if level not in ['junior', 'mid', 'senior']:
            return Response(
                {'error': 'level must be junior, mid, or senior'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if interview_type not in ['hr', 'technical', 'case', 'mixed']:
            return Response(
                {'error': 'type must be hr, technical, case, or mixed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get role
        try:
            role = RoleCatalog.objects.get(id=role_id)
        except RoleCatalog.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get profile if provided
        profile = None
        if profile_id:
            try:
                profile = Profile.objects.get(id=profile_id, user=request.user)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create session
        session = InterviewSession.objects.create(
            user=request.user,
            profile=profile,
            role_selected=role,
            role_source=role_source,
            level=level,
            type=interview_type,
            status='created'
        )
        
        # Generate questions
        try:
            generate_interview_questions(str(session.id))
            session.status = 'in_progress'
            session.save()
        except Exception as e:
            return Response(
                {'error': f'Error generating questions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InterviewSessionDetailView(generics.RetrieveAPIView):
    """Get interview session details."""
    permission_classes = [IsAuthenticated, IsAuthenticatedOwner]
    serializer_class = InterviewSessionSerializer
    queryset = InterviewSession.objects.all()
    lookup_field = 'id'


class InterviewFinishView(generics.UpdateAPIView):
    """Finish an interview session and calculate overall score."""
    permission_classes = [IsAuthenticated, IsAuthenticatedOwner]
    serializer_class = InterviewSessionSerializer
    queryset = InterviewSession.objects.all()
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        session = self.get_object()
        
        if session.status == 'completed':
            return Response(
                {'error': 'Session already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate overall score from all answers
        from ..services.report import aggregate_scores
        from ..services.scorer import calculate_overall_score
        
        rubric_scores = aggregate_scores(session)
        overall_score = calculate_overall_score(rubric_scores)
        
        # Update session
        session.overall_score = overall_score
        session.status = 'completed'
        session.ended_at = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)

