from django.contrib import admin
from .models import InterviewSession, InterviewQuestion, InterviewAnswer


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role_selected', 'type', 'level', 'status', 'overall_score', 'created_at']
    list_filter = ['status', 'type', 'level', 'created_at']
    search_fields = ['user__email', 'role_selected__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'order', 'category', 'difficulty', 'created_at']
    list_filter = ['category', 'difficulty', 'created_at']
    search_fields = ['question_text', 'session__user__email']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(InterviewAnswer)
class InterviewAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'time_seconds', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['answer_text', 'question__session__user__email']
    readonly_fields = ['id', 'submitted_at', 'created_at']
    date_hierarchy = 'submitted_at'
