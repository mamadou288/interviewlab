from django.db import models
from django.conf import settings
import uuid


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    cv_document = models.ForeignKey(
        'profiles.CVDocument',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles'
    )
    data_json = models.JSONField(default=dict)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Profile for {self.user.email}"

