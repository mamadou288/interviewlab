from django.urls import path
from .views import RoleListView, RoleSuggestionsView

app_name = 'roles'

urlpatterns = [
    path('roles', RoleListView.as_view(), name='role-list'),
    path('cv/<uuid:cv_id>/role-suggestions', RoleSuggestionsView.as_view(), name='role-suggestions'),
]

