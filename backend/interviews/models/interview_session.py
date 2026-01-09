from django.db import models
from django.conf import settings
import uuid


class InterviewSession(models.Model):
    ROLE_SOURCE_CHOICES = [
        ('suggestion', 'Suggestion'),
        ('catalog', 'Catalog'),
        ('custom', 'Custom'),
    ]
    
    LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('mid', 'Mid-level'),
        ('senior', 'Senior'),
    ]
    
    TYPE_CHOICES = [
        ('hr', 'HR'),
        ('technical', 'Technical'),
        ('case', 'Case Study'),
        ('mixed', 'Mixed'),
    ]
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interview_sessions'
    )
    role_selected = models.ForeignKey(
        'roles.RoleCatalog',
        on_delete=models.PROTECT,
        related_name='interview_sessions'
    )
    role_source = models.CharField(max_length=20, choices=ROLE_SOURCE_CHOICES, default='catalog')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    overall_score = models.IntegerField(null=True, blank=True, help_text="Score from 0-100")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_sessions'
        verbose_name = 'Interview Session'
        verbose_name_plural = 'Interview Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.role_selected.name} ({self.type})"

