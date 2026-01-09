from django.db import models
import uuid


class UpgradePlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='upgrade_plans'
    )
    duration_days = models.PositiveIntegerField(help_text="7 or 14 days")
    plan_json = models.JSONField(
        default=dict,
        help_text="Complete plan structure with strengths, weaknesses, learning_objectives, daily_plans, next_interview"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'upgrade_plans'
        verbose_name = 'Upgrade Plan'
        verbose_name_plural = 'Upgrade Plans'
        unique_together = ['session', 'duration_days']
        ordering = ['-created_at']

    def __str__(self):
        return f"Upgrade Plan for {self.session} ({self.duration_days} days)"

