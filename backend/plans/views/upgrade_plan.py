from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAuthenticatedOwner
from interviews.models import InterviewSession
from ..models import UpgradePlan
from ..serializers import UpgradePlanSerializer
from ..services.generator import generate_upgrade_plan


class UpgradePlanView(generics.RetrieveAPIView):
    """
    Generate or retrieve upgrade plan for an interview session.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpgradePlanSerializer
    
    def retrieve(self, request, *args, **kwargs):
        session_id = self.kwargs['id']
        duration_days = request.query_params.get('duration_days', '7')
        
        # Validate duration_days
        try:
            duration_days = int(duration_days)
            if duration_days not in [7, 14]:
                return Response(
                    {'error': 'duration_days must be 7 or 14'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'duration_days must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get session and check ownership
        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            return Response(
                {'error': 'Interview session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if session.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if session is completed
        if session.status != 'completed':
            return Response(
                {'error': 'Interview session must be completed to generate upgrade plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if UpgradePlan exists for this session and duration
        try:
            upgrade_plan = UpgradePlan.objects.get(session=session, duration_days=duration_days)
        except UpgradePlan.DoesNotExist:
            # Generate new plan
            try:
                upgrade_plan = generate_upgrade_plan(str(session_id), duration_days)
            except Exception as e:
                return Response(
                    {'error': f'Error generating upgrade plan: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        serializer = self.get_serializer(upgrade_plan)
        return Response(serializer.data)

