from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid


class CVDocument(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cv_documents'
    )
    file = models.FileField(upload_to='cv_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    extracted_text = models.TextField(null=True, blank=True)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cv_documents'
        verbose_name = 'CV Document'
        verbose_name_plural = 'CV Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.file.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Validate file on save
        if self.file:
            # Set file size if not already set
            if not self.file_size:
                self.file_size = self.file.size
            
            # Set mime type if not already set
            if not self.mime_type:
                self.mime_type = getattr(self.file, 'content_type', '')
        
        super().save(*args, **kwargs)

