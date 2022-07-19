from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

USER_STATUSES = [
    ('beginner', 'beginner'),
    ('Amateur', 'Amateur'),
    ('PRO', 'PRO'),
    ('KING', 'KING'),
]


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
    incorrect_answers = models.CharField(blank=True, max_length=1000)
    answer1 = models.CharField(blank=True, max_length=300)
    answer2 = models.CharField(blank=True, max_length=300)
    answer3 = models.CharField(blank=True, max_length=300)
    answer4 = models.CharField(blank=True, max_length=300)


class Status(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=150,
        blank=False,
        choices=USER_STATUSES,
        default='beginner',
    )
