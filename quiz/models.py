# quiz/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class QuestionType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text="Name of the icon from heroicons", default="academic-cap")
    sample_question = models.TextField(help_text="A sample question to show in the preview card")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Question Type"
        verbose_name_plural = "Question Types"

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard')
    ]

    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='questions')
    question_context = models.TextField(
        help_text="The passage or context that precedes the question (e.g., reading passage, scenario description)",
        blank=True,
        null=True
    )
    text = models.TextField(help_text="The actual question text")
    image = models.ImageField(upload_to='question_images/', null=True, blank=True, 
                            help_text="Optional image for the question")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1)
    explanation = models.TextField(help_text="Explanation of the correct answer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    average_time = models.FloatField(default=0, help_text="Average time taken to answer in seconds")
    success_rate = models.FloatField(default=0, help_text="Percentage of correct answers")

    def __str__(self):
        return f"{self.question_type.name} - {self.text[:50]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def update_statistics(self, time_taken, is_correct):
        """Update question statistics after each attempt"""
        self.usage_count += 1
        self.average_time = (
            (self.average_time * (self.usage_count - 1) + time_taken) / self.usage_count
        )
        total_correct = (self.success_rate * (self.usage_count - 1)) + (1 if is_correct else 0)
        self.success_rate = (total_correct / self.usage_count) * 100
        self.save()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"

    def clean(self):
        """Ensure only one correct answer per question"""
        if self.is_correct and self.question_id is not None:
            correct_choices = Choice.objects.filter(
                question=self.question, 
                is_correct=True
            ).exclude(id=self.id)
            if correct_choices.exists():
                raise ValidationError("This question already has a correct answer.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=models.Q(is_correct=True),
                name='unique_correct_choice'
            )
        ]

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_question_types = models.ManyToManyField(QuestionType)
    preferred_time_limit = models.IntegerField(default=30)
    preferred_question_count = models.IntegerField(default=10)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    time_taken = models.FloatField(help_text="Time taken to answer in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        self.question.update_statistics(self.time_taken, self.is_correct)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Session settings
    question_types = models.ManyToManyField(QuestionType)
    number_of_questions = models.IntegerField()
    time_limit = models.IntegerField(help_text="Time limit in minutes")
    
    # Session progress
    is_completed = models.BooleanField(default=False)
    current_question_index = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Practice Session {self.id} - {self.user.username}"
    
    @property
    def score(self):
        if not self.is_completed:
            return None
        correct_answers = PracticeAnswer.objects.filter(
            session=self, 
            is_correct=True
        ).count()
        return (correct_answers / self.number_of_questions) * 100

class PracticeAnswer(models.Model):
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    time_taken = models.FloatField(help_text="Time taken in seconds")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)