from django.contrib import admin
from .models import CVDocument, Profile


@admin.register(CVDocument)
class CVDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'file_size', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']
    date_hierarchy = 'created_at'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'confirmed', 'created_at']
    list_filter = ['confirmed', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
