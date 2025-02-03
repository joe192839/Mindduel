from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta
from django_countries.fields import CountryField  

class MinduelUser(AbstractUser):
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    country_code = CountryField(blank=True, null=True)  
    
    def __str__(self):
        return self.username

class UserPerformanceMetrics(models.Model):
    user = models.OneToOneField(
        MinduelUser, 
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    # Category-specific metrics
    logical_reasoning_accuracy = models.FloatField(default=0.0)
    verbal_linguistic_accuracy = models.FloatField(default=0.0)
    spatial_reasoning_accuracy = models.FloatField(default=0.0)
    critical_thinking_accuracy = models.FloatField(default=0.0)
    
    # New total/correct fields for each category
    logical_reasoning_correct = models.IntegerField(default=0)
    logical_reasoning_total = models.IntegerField(default=0)
    
    verbal_linguistic_correct = models.IntegerField(default=0)
    verbal_linguistic_total = models.IntegerField(default=0)
    
    spatial_reasoning_correct = models.IntegerField(default=0)
    spatial_reasoning_total = models.IntegerField(default=0)
    
    critical_thinking_correct = models.IntegerField(default=0)
    critical_thinking_total = models.IntegerField(default=0)
    
    # Time-based metrics
    avg_response_time = models.FloatField(default=0.0)
    fastest_correct_answer = models.FloatField(null=True)
    slowest_correct_answer = models.FloatField(null=True)
    
    # Progress metrics
    total_questions_answered = models.IntegerField(default=0)
    correct_answers_streak = models.IntegerField(default=0)
    highest_streak = models.IntegerField(default=0)
    
    # Improvement tracking
    weekly_improvement_rate = models.FloatField(default=0.0)
    monthly_improvement_rate = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = "User Performance Metrics"

    def __str__(self):
        return f"Metrics for {self.user.username}"

    @classmethod
    def update_user_metrics(cls, user):
        """Update or create metrics for a user based on their recent performance"""
        metrics, _ = cls.objects.get_or_create(user=user)
        
        # Get user's answers from the last 30 days
        from quickplay.models import QuickplayAnswer
        recent_answers = QuickplayAnswer.objects.filter(
            game__player=user,
            answered_at__gte=timezone.now() - timedelta(days=30)
        )
        
        # Update category metrics
        for category in ['logical_reasoning', 'verbal_linguistic', 'spatial_reasoning', 'critical_thinking']:
            category_answers = recent_answers.filter(question__category=category)
            if category_answers.exists():
                total = category_answers.count()
                correct = category_answers.filter(is_correct=True).count()
                
                # Update total and correct counts
                setattr(metrics, f"{category}_total", total)
                setattr(metrics, f"{category}_correct", correct)
                
                # Calculate and set accuracy
                accuracy = (correct / total * 100)
                setattr(metrics, f"{category}_accuracy", accuracy)
        
        # Update time-based metrics
        if recent_answers.exists():
            metrics.avg_response_time = recent_answers.aggregate(Avg('response_time'))['response_time__avg']
            correct_answers = recent_answers.filter(is_correct=True)
            if correct_answers.exists():
                metrics.fastest_correct_answer = correct_answers.order_by('response_time').first().response_time
                metrics.slowest_correct_answer = correct_answers.order_by('-response_time').first().response_time
                
        # Update progress metrics
        metrics.total_questions_answered = recent_answers.count()
        
        # Calculate current streak
        ordered_answers = recent_answers.order_by('-answered_at')
        current_streak = 0
        for answer in ordered_answers:
            if answer.is_correct:
                current_streak += 1
            else:
                break
        
        metrics.correct_answers_streak = current_streak
        metrics.highest_streak = max(metrics.highest_streak, current_streak)
        
        # Calculate improvement rates
        old_answers = QuickplayAnswer.objects.filter(
            game__player=user,
            answered_at__lt=timezone.now() - timedelta(days=7)
        )
        
        if old_answers.exists():
            old_accuracy = old_answers.filter(is_correct=True).count() / old_answers.count() * 100
            current_accuracy = metrics.total_questions_answered > 0 and \
                (recent_answers.filter(is_correct=True).count() / metrics.total_questions_answered * 100)
            
            if current_accuracy:
                metrics.weekly_improvement_rate = current_accuracy - old_accuracy
        
        metrics.save()
        return metrics

class GlobalGameMetrics(models.Model):
    date = models.DateField(unique=True)
    total_games_played = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0.0)
    avg_completion_time = models.FloatField(default=0.0)
    
    # Category-specific global metrics
    category_accuracies = models.JSONField(default=dict)
    category_response_times = models.JSONField(default=dict)
    
    # Difficulty distribution
    difficulty_distribution = models.JSONField(default=dict)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Global Game Metrics"

    def __str__(self):
        return f"Global Metrics for {self.date}"

    @classmethod
    def update_daily_metrics(cls):
        """Update or create global metrics for the current day"""
        today = timezone.now().date()
        metrics, _ = cls.objects.get_or_create(date=today)
        
        # Get today's games
        from quickplay.models import QuickplayGame, QuickplayAnswer
        today_games = QuickplayGame.objects.filter(
            start_time__date=today,
            is_completed=True
        )
        
        if today_games.exists():
            metrics.total_games_played = today_games.count()
            metrics.avg_score = today_games.aggregate(Avg('score'))['score__avg'] or 0
            
            # Calculate completion times
            completion_times = [
                (game.end_time - game.start_time).total_seconds()
                for game in today_games if game.end_time
            ]
            
            if completion_times:
                metrics.avg_completion_time = sum(completion_times) / len(completion_times)
            
            # Update category metrics
            category_stats = {}
            for category in ['logical_reasoning', 'verbal_linguistic', 'spatial_reasoning', 'critical_thinking']:
                category_answers = QuickplayAnswer.objects.filter(
                    game__in=today_games,
                    question__category=category
                )
                if category_answers.exists():
                    category_stats[category] = {
                        'accuracy': (category_answers.filter(is_correct=True).count() / 
                                   category_answers.count() * 100),
                        'avg_response_time': category_answers.aggregate(
                            Avg('response_time'))['response_time__avg'] or 0
                    }
            
            metrics.category_accuracies = category_stats
            
            # Update difficulty distribution
            difficulty_counts = QuickplayAnswer.objects.filter(
                game__in=today_games
            ).values('question__difficulty').annotate(
                count=models.Count('id')
            )
            
            metrics.difficulty_distribution = {
                item['question__difficulty']: item['count']
                for item in difficulty_counts
            }
            
            metrics.save()
        
        return metrics