from django.db import models
import uuid


class InterviewQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('hr', 'HR'),
        ('technical', 'Technical'),
        ('case', 'Case Study'),
        ('behavioral', 'Behavioral'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='questions'
    )
    order = models.PositiveIntegerField(help_text="Question sequence number")
    question_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    skill_tags_json = models.JSONField(
        default=list,
        help_text="List of skill tags assessed by this question"
    )
    is_followup = models.BooleanField(default=False)
    parent_question = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='followup_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interview_questions'
        verbose_name = 'Interview Question'
        verbose_name_plural = 'Interview Questions'
        unique_together = ['session', 'order']
        ordering = ['session', 'order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

