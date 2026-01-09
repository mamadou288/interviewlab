from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from profiles.models import CVDocument
from ..models import RoleSuggestion
from ..serializers import RoleSuggestionSerializer
from ..services.suggester import suggest_roles


class RoleSuggestionsView(generics.ListAPIView):
    """
    View for retrieving role suggestions for a CV document.
    Generates suggestions if they don't exist.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSuggestionSerializer
    
    def get_queryset(self):
        cv_id = self.kwargs['cv_id']
        return RoleSuggestion.objects.filter(cv_document_id=cv_id).select_related('role')
    
    def list(self, request, *args, **kwargs):
        cv_id = self.kwargs['cv_id']
        
        # Get CVDocument and check ownership
        try:
            cv_document = CVDocument.objects.get(id=cv_id)
        except CVDocument.DoesNotExist:
            return Response(
                {'error': 'CV document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions - user must own the CV document
        if cv_document.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if suggestions exist
        existing_suggestions = RoleSuggestion.objects.filter(cv_document=cv_document)
        
        # If no suggestions exist, generate them
        if not existing_suggestions.exists():
            suggestions = suggest_roles(str(cv_id))
        else:
            suggestions = existing_suggestions.all()
        
        # Serialize and return
        serializer = self.get_serializer(suggestions, many=True)
        return Response({
            'suggestions': serializer.data,
            'count': len(serializer.data)
        })

