from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from ..models import RoleCatalog
from ..serializers import RoleCatalogSerializer


class RoleListView(generics.ListAPIView):
    """
    View for listing and searching roles.
    Supports filtering by category and searching by name/description.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleCatalogSerializer
    queryset = RoleCatalog.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

