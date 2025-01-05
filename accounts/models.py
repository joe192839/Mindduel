from django.db import models
from django.contrib.auth.models import AbstractUser

class MinduelUser(AbstractUser):
    total_score = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    last_played = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username