from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseServerError
from django.urls import reverse_lazy
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
        if not Question.objects.filter(user=request.user).exists():
            return redirect(reverse_lazy('app:quiz'))
        question = get_object_or_404(Question, user=request.user)
        user_answer = request.POST.get('user_answer')
        if question.question != request.POST.get('question'):
            return redirect(reverse_lazy('app:quiz'))
        if question.correct_answer == user_answer and question.question == request.POST.get('question'):
            current_score += 1
            score.score = current_score
            score.save()
        correct_answer = question.correct_answer
        text = question.question
        question.delete()
        return render(request, template_name='quiz.html',
                      context={'correct_answer': correct_answer,
                               'results': [{'question': text}],
                               'score': score,
                               'is_answered': True,
                               }
                      )
    url = 'https://opentdb.com/api.php?amount=1&type=boolean'
    try:
        response = requests.get(url)
    except Exception as error:
        return HttpResponseServerError(error)
    if not response.status_code == 200:
        return HttpResponseServerError('Service not available. Please try again later')
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


@login_required
def quiz_multiple(request):
    if not Score.objects.filter(user=request.user).exists():
        Score.objects.create(user=request.user)
    score = Score.objects.get(user=request.user)
    current_score = score.score

    if request.method == 'POST':
        if not Question.objects.filter(user=request.user).exists():
            return redirect(reverse_lazy('app:quiz_multiple'))
        question = Question.objects.get(user=request.user)
        user_answer = request.POST.get('user_answer')
        is_answered = False
        if question.question != request.POST.get('question'):
            return redirect(reverse_lazy('app:quiz_multiple'))
        if question.correct_answer == user_answer and question.question == request.POST.get('question'):
            current_score += 5
            score.score = current_score
            score.save()
            is_answered = True
        correct_answer = question.correct_answer
        text = question.question
        answers = [question.answer1, question.answer2, question.answer3, question.answer4]
        question.delete()
        return render(request, template_name='quiz_multiple.html',
                      context={'correct_answer': correct_answer,
                               'results': [{'question': text, }],
                               'answers': answers,
                               'score': score,
                               'is_answered': is_answered,
                               'is_post': True,
                               }
                      )

    url = 'https://opentdb.com/api.php?amount=1&type=multiple'
    try:
        response = requests.get(url)
    except Exception as error:
        return HttpResponseServerError(error)
    if not response.status_code == 200:
        return HttpResponseServerError('Service not available. Please try again later')
    json = response.json()
    if not Question.objects.filter(user=request.user).exists():
        Question.objects.create(user=request.user)
    question = Question.objects.get(user=request.user)
    question.category = json['results'][0]['category']
    question.type = json['results'][0]['type']
    question.difficulty = json['results'][0]['difficulty']
    question.question = json['results'][0]['question']
    question.correct_answer = json['results'][0]['correct_answer']
    question.incorrect_answers = json['results'][0]['incorrect_answers']
    all_answers = list({*json['results'][0]['incorrect_answers'], json['results'][0]['correct_answer']})
    question.answer1 = all_answers[0]
    question.answer2 = all_answers[1]
    question.answer3 = all_answers[2]
    question.answer4 = all_answers[3]
    question.save()
    context = {'results': json['results'],
               'score': score,
               'answers': [question.answer1, question.answer2, question.answer3, question.answer4],
               }

    return render(request, template_name='quiz_multiple.html', context=context)
