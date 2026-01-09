from django.contrib import admin
from .models import RoleCatalog, RoleSuggestion


@admin.register(RoleCatalog)
class RoleCatalogAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(RoleSuggestion)
class RoleSuggestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'cv_document', 'role', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['role__name', 'cv_document__user__email']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'
