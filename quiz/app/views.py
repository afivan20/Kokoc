from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import requests
from users.models import Score, Question


def index(request):
    if request.user.is_authenticated:
        if not Score.objects.filter(user=request.user).exists():
            Score.objects.create(user=request.user)
        score = Score.objects.get(user=request.user)
        return render(request, template_name='index.html', context={'score': score})
    return render(request, template_name='index.html',)


def top(request):
    # top_scores = (Score.objects.order_by('-score').values_list('score', flat=True).distinct())
    # users = Score.objects.order_by('-score').filter(score__in=top_scores[:10])
    users = Score.objects.order_by('-score')[:10]
    if request.user.is_authenticated:
        if not Score.objects.filter(user=request.user).exists():
            Score.objects.create(user=request.user)
        score = Score.objects.get(user=request.user)
        return render(request, template_name='top.html', context={'score': score, 'users': users})
    return render(request, template_name='top.html', context={'users': users})


@login_required
def quiz(request):
    if not Score.objects.filter(user=request.user).exists():
        Score.objects.create(user=request.user)
    score = Score.objects.get(user=request.user)
    current_score = score.score
    if request.method == 'POST':
        question = get_object_or_404(Question, user=request.user)
        user_answer = request.POST.get('user_answer')
        if question.correct_answer == user_answer and question.question == request.POST.get('question'):
            current_score += 1
            score.score = current_score
            score.save()
        correct_answer = question.correct_answer
        text = question.question
        question.question = ''
        question.save()
        return render(request, template_name='quiz.html',
                      context={'correct_answer': correct_answer,
                               'results': [{'question': text}],
                               'score': score,
                               'is_answered': True,
                               }
                      )

    url = 'https://opentdb.com/api.php?amount=1&type=boolean'
    response = requests.get(url)
    json = response.json()
    if not Question.objects.filter(user=request.user).exists():
        Question.objects.create(user=request.user)
    question = Question.objects.get(user=request.user)
    question.category = json['results'][0]['category']
    question.type = json['results'][0]['type']
    question.difficulty = json['results'][0]['difficulty']
    question.question = json['results'][0]['question']
    question.correct_answer = json['results'][0]['correct_answer']
    question.save()
    context = {'results': json['results'],
               'score': score,
               }

    return render(request, template_name='quiz.html', context=context)
