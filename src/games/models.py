# In your games/models.py file

from django.db import models
from django.contrib.auth.models import User


class Score(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "-created_on"]

    def __str__(self):
        return f"{self.player.username} - {self.score}"
