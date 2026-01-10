from django.urls import path
from .views import UploadCVView, CVDocumentDetailView, ProfileView
from .views.job_posting import ParseJobPostingView

app_name = 'profiles'

urlpatterns = [
    path('cv/upload', UploadCVView.as_view(), name='cv-upload'),
    path('cv/<uuid:id>', CVDocumentDetailView.as_view(), name='cv-detail'),
    path('profile/me', ProfileView.as_view(), name='profile-me'),
    path('job-posting/parse', ParseJobPostingView.as_view(), name='job-posting-parse'),
]

