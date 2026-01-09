from django.urls import path
from .views import UploadCVView, CVDocumentDetailView, ProfileView

app_name = 'profiles'

urlpatterns = [
    path('cv/upload', UploadCVView.as_view(), name='cv-upload'),
    path('cv/<uuid:id>', CVDocumentDetailView.as_view(), name='cv-detail'),
    path('profile/me', ProfileView.as_view(), name='profile-me'),
]

