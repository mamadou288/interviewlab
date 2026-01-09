from django.urls import path
from .views import UpgradePlanView

app_name = 'plans'

urlpatterns = [
    path('interviews/<uuid:id>/upgrade-plan', UpgradePlanView.as_view(), name='upgrade-plan'),
]

