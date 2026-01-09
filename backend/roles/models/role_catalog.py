from django.db import models
import uuid


class RoleCatalog(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('fullstack', 'Full-stack'),
        ('devops', 'DevOps'),
        ('data', 'Data'),
        ('product', 'Product'),
        ('design', 'Design'),
        ('mobile', 'Mobile'),
        ('qa', 'QA'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    keywords_json = models.JSONField(default=list, help_text="List of keywords for matching")
    description = models.TextField(blank=True)
    level_keywords_json = models.JSONField(
        default=dict,
        help_text="Keywords for different experience levels",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_catalog'
        verbose_name = 'Role Catalog'
        verbose_name_plural = 'Role Catalog'
        ordering = ['name']

    def __str__(self):
        return self.name

