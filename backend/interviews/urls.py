from django.urls import path
from .views import (
    InterviewSessionCreateView,
    InterviewSessionDetailView,
    InterviewQuestionsView,
    InterviewAnswerView,
    InterviewFinishView,
    InterviewReportView,
)

app_name = 'interviews'

urlpatterns = [
    path('interviews', InterviewSessionCreateView.as_view(), name='interview-create'),
    path('interviews/<uuid:id>', InterviewSessionDetailView.as_view(), name='interview-detail'),
    path('interviews/<uuid:id>/questions', InterviewQuestionsView.as_view(), name='interview-questions'),
    path('interviews/<uuid:id>/answers', InterviewAnswerView.as_view(), name='interview-answer'),
    path('interviews/<uuid:id>/finish', InterviewFinishView.as_view(), name='interview-finish'),
    path('interviews/<uuid:id>/report', InterviewReportView.as_view(), name='interview-report'),
]

