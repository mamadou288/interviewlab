from django.db import models
import uuid


class RoleSuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cv_document = models.ForeignKey(
        'profiles.CVDocument',
        on_delete=models.CASCADE,
        related_name='role_suggestions'
    )
    role = models.ForeignKey(
        'roles.RoleCatalog',
        on_delete=models.CASCADE,
        related_name='suggestions'
    )
    score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        help_text="Similarity score from 0.00 to 1.00"
    )
    reasons_json = models.JSONField(
        default=list,
        help_text="List of reasons for this suggestion"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_suggestions'
        verbose_name = 'Role Suggestion'
        verbose_name_plural = 'Role Suggestions'
        unique_together = ['cv_document', 'role']
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"{self.cv_document.user.email} - {self.role.name} ({self.score})"

