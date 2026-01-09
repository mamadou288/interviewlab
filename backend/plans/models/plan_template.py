from django.db import models
import uuid


class PlanTemplate(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill_tag = models.CharField(max_length=100, unique=True, help_text="e.g., 'communication.star', 'backend.django.auth'")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    steps_json = models.JSONField(
        default=list,
        help_text="Daily plan structure array with day, topic, drills, mini_mock, quick_test"
    )
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.PositiveIntegerField(help_text="Estimated time per day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plan_templates'
        verbose_name = 'Plan Template'
        verbose_name_plural = 'Plan Templates'
        ordering = ['skill_tag']

    def __str__(self):
        return f"{self.title} ({self.skill_tag})"

