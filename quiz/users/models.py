from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Score(models.Model):
    score = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Question(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category = models.CharField(blank=True, max_length=300)
    type = models.CharField(blank=True, max_length=300)
    difficulty = models.CharField(blank=True, max_length=100)
    question = models.CharField(blank=True, max_length=500)
    correct_answer = models.CharField(blank=True, max_length=100)