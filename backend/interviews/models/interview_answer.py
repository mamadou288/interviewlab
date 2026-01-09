from django.db import models
import uuid


class InterviewAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(
        'interviews.InterviewQuestion',
        on_delete=models.CASCADE,
        related_name='answer'
    )
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    time_seconds = models.PositiveIntegerField(help_text="Time taken to answer in seconds")
    scores_json = models.JSONField(
        default=dict,
        help_text="Rubric scores: structure, relevance, technical_accuracy, depth, communication"
    )
    feedback_json = models.JSONField(
        default=dict,
        help_text="Generated feedback: strengths, weaknesses, improvements"
    )
    skill_tags_json = models.JSONField(
        default=list,
        help_text="Skills assessed in this answer"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interview_answers'
        verbose_name = 'Interview Answer'
        verbose_name_plural = 'Interview Answers'
        ordering = ['submitted_at']

    def __str__(self):
        return f"Answer to Q{self.question.order} - {self.question.session}"

