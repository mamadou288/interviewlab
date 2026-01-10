from django.urls import path
from .views import AnalyticsOverviewView, AnalyticsSkillsView, AnalyticsSessionsView

app_name = 'analytics'

urlpatterns = [
    path('analytics/overview', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('analytics/skills', AnalyticsSkillsView.as_view(), name='analytics-skills'),
    path('analytics/sessions', AnalyticsSessionsView.as_view(), name='analytics-sessions'),
]

