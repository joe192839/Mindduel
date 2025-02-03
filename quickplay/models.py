from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Count, F, ExpressionWrapper, fields
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class QuickplayQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    CATEGORY_CHOICES = [
        ('logical_reasoning', 'Logical Reasoning'),
        ('verbal_linguistic', 'Verbal Linguistic'),
        ('spatial_reasoning', 'Spatial Reasoning'),
        ('critical_thinking', 'Critical Thinking')
    ]
    question_text = models.TextField()
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200)
    option_4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    explanation = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='reasoning')
    target_response_time = models.FloatField(null=True, blank=True, help_text="Target time to answer in seconds")
    
    def __str__(self):
        return f"{self.question_text[:50]}..."

    class Meta:
        ordering = ['id']

class AIQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    CATEGORY_CHOICES = [
        ('logical_reasoning', 'Logical Reasoning'),
        ('quantitative_reasoning', 'Quantitative Reasoning'),
        ('linguistic_reasoning', 'Linguistic Reasoning'),
        ('spatial_reasoning', 'Spatial Reasoning')
    ]
    
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    wrong_answers = models.JSONField()  # Store alternative answers
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    times_used = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.question_text[:50]}..."

    class Meta:
        ordering = ['-created_at']

class QuickplayGame(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    lives_remaining = models.IntegerField(default=3)
    is_completed = models.BooleanField(default=False)
    time_limit = models.IntegerField(default=300)  # 5 minutes in seconds
    highest_speed_level = models.IntegerField(default=60)
    
    # ManyToManyField for categories
    categories = models.ManyToManyField(Category, related_name='games', blank=True)
    
    # Legacy field renamed to categories_string
    categories_string = models.CharField(max_length=255, blank=True, 
                                       help_text="Comma-separated list of selected categories")

    # New analytics fields
    total_response_time = models.FloatField(default=0.0, help_text="Total time spent answering questions")
    breaks_taken = models.IntegerField(default=0, help_text="Number of breaks taken during game")
    device_info = models.JSONField(default=dict, help_text="Information about user's device")
    interaction_patterns = models.JSONField(default=dict, help_text="User interaction patterns during game")

    def save(self, *args, **kwargs):
        # Save the game first
        super().save(*args, **kwargs)
        
        # If the game is completed, update metrics
        if self.is_completed:
            print(f"Updating metrics for completed game {self.id}")
            from accounts.models import UserPerformanceMetrics
            UserPerformanceMetrics.update_user_metrics(self.player)

    def __str__(self):
        return f"Game by {self.player.username} - Score: {self.score}"

    def get_categories_list(self):
        """Return the categories as a list"""
        if self.categories.exists():
            return list(self.categories.values_list('name', flat=True))
        return [cat.strip() for cat in self.categories_string.split(',')] if self.categories_string else []

    def calculate_metrics(self):
        """Calculate game performance metrics"""
        answers = self.quickplayanswer_set.all()
        metrics = {
            'total_questions': answers.count(),
            'correct_answers': answers.filter(is_correct=True).count(),
            'avg_response_time': answers.aggregate(Avg('response_time'))['response_time__avg'] or 0,
            'category_performance': {}
        }
        
        # Calculate category-specific metrics
        for category in QuickplayQuestion.CATEGORY_CHOICES:
            category_answers = answers.filter(question__category=category[0])
            if category_answers.exists():
                metrics['category_performance'][category[0]] = {
                    'total': category_answers.count(),
                    'correct': category_answers.filter(is_correct=True).count(),
                    'avg_time': category_answers.aggregate(Avg('response_time'))['response_time__avg'] or 0
                }
        
        return metrics

    class Meta:
        ordering = ['-start_time']

class QuickplayAnswer(models.Model):
    game = models.ForeignKey(QuickplayGame, on_delete=models.CASCADE)
    question = models.ForeignKey(QuickplayQuestion, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)
    
    # New analytics fields
    response_time = models.FloatField(default=0.0, help_text="Time taken to answer in seconds")
    confidence_level = models.IntegerField(default=0, help_text="User's confidence level 1-5")
    answer_changed = models.BooleanField(default=False, help_text="Whether user changed their answer")
    initial_answer = models.CharField(max_length=200, null=True, blank=True)
    interaction_data = models.JSONField(default=dict, help_text="Detailed interaction data during answering")

    def __str__(self):
        return f"Answer for {self.game.player.username} - Correct: {self.is_correct}"

    @property
    def was_within_target_time(self):
        target_time = self.question.target_response_time
        return self.response_time <= target_time if target_time else None

    class Meta:
        ordering = ['answered_at']

class Leaderboard(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_achieved = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField()  # in seconds

    def __str__(self):
        return f"{self.player.username} - Score: {self.score}"

    class Meta:
        ordering = ['-score', 'time_taken']
        verbose_name_plural = "Leaderboard Entries"