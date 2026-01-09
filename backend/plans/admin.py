from django.contrib import admin
from .models import PlanTemplate, UpgradePlan


@admin.register(PlanTemplate)
class PlanTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'skill_tag', 'title', 'difficulty', 'duration_minutes', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['skill_tag', 'title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(UpgradePlan)
class UpgradePlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'duration_days', 'created_at']
    list_filter = ['duration_days', 'created_at']
    search_fields = ['session__user__email', 'session__role_selected__name']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
