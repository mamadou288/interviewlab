from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from ..serializers import ProfileSerializer, ProfileUpdateSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user's profile.
    Creates empty profile if doesn't exist.
    GET /api/profile/me - Retrieve profile
    PATCH /api/profile/me - Update profile
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ProfileUpdateSerializer
        return ProfileSerializer
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={'data_json': {}}
        )
        return profile

