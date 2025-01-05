from django.db import models
from django.conf import settings  # Add this import

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

    def __str__(self):
        return f"{self.question_text[:50]}..."

    class Meta:
        ordering = ['id']

class QuickplayGame(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    lives_remaining = models.IntegerField(default=3)
    is_completed = models.BooleanField(default=False)
    time_limit = models.IntegerField(default=300)  # 5 minutes in seconds
    categories = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of selected categories")
    highest_speed_level = models.IntegerField(default=60)  # Added field for highest speed level

    def __str__(self):
        return f"Game by {self.player.username} - Score: {self.score}"

    def get_categories_list(self):
        """Return the categories as a list"""
        return [cat.strip() for cat in self.categories.split(',')] if self.categories else []

    class Meta:
        ordering = ['-start_time']

class QuickplayAnswer(models.Model):
    game = models.ForeignKey(QuickplayGame, on_delete=models.CASCADE)
    question = models.ForeignKey(QuickplayQuestion, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for {self.game.player.username} - Correct: {self.is_correct}"

    class Meta:
        ordering = ['answered_at']

class Leaderboard(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated
    score = models.IntegerField()
    date_achieved = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField()  # in seconds

    def __str__(self):
        return f"{self.player.username} - Score: {self.score}"

    class Meta:
        ordering = ['-score', 'time_taken']
        verbose_name_plural = "Leaderboard Entries"