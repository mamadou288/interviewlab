from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from users.permissions import IsAuthenticatedOwner
from ..models import CVDocument, Profile
from ..serializers import CVDocumentSerializer
from ..services.parser import validate_file, extract_text
from ..services.extractor import extract_profile_data


class UploadCVView(generics.CreateAPIView):
    """
    View for uploading CV documents.
    Accepts multipart/form-data with 'file' field.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CVDocumentSerializer
    
    def create(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Validate file
        try:
            validate_file(file)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create CVDocument
        cv_document = CVDocument.objects.create(
            user=request.user,
            file=file,
            status='uploaded',
            file_size=file.size,
            mime_type=getattr(file, 'content_type', '')
        )
        
        # Process file synchronously
        try:
            cv_document.status = 'processing'
            cv_document.save()
            
            # Extract text
            extracted_text = extract_text(file)
            cv_document.extracted_text = extracted_text
            
            # Extract profile data using LLM
            profile_data = extract_profile_data(extracted_text)
            
            # Find or create role based on extracted primary_role
            if profile_data.get('primary_role'):
                from roles.services.role_creator import find_or_create_role
                role, role_created = find_or_create_role(
                    role_name=profile_data['primary_role'],
                    category=profile_data.get('role_category', 'other'),
                    skills=profile_data.get('skills', [])
                )
                # Store role_id in profile_data for easy access
                if role:
                    profile_data['detected_role_id'] = str(role.id)
                    profile_data['detected_role_name'] = role.name
            
            # Create or update Profile
            profile, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={'data_json': profile_data}
            )
            
            if not created:
                # Update existing profile
                profile.data_json = profile_data
                profile.cv_document = cv_document
                profile.save()
            else:
                profile.cv_document = cv_document
                profile.save()
            
            # Update CVDocument status
            cv_document.status = 'completed'
            cv_document.processed_at = timezone.now()
            cv_document.save()
            
        except Exception as e:
            cv_document.status = 'failed'
            cv_document.save()
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(cv_document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CVDocumentDetailView(generics.RetrieveAPIView):
    """
    View for retrieving CV document details.
    """
    permission_classes = [IsAuthenticated, IsAuthenticatedOwner]
    serializer_class = CVDocumentSerializer
    queryset = CVDocument.objects.all()
    lookup_field = 'id'

