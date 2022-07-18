from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseServerError
from django.urls import reverse_lazy
import requests
from users.models import Score, Question, Status


def index(request):
    if request.user.is_authenticated:
        if not Status.objects.filter(user=request.user).exists():
            Status.objects.create(user=request.user, status='beginner')
        status = Status.objects.get(user=request.user)
        if not Score.objects.filter(user=request.user).exists():
            Score.objects.create(user=request.user)
        score = Score.objects.get(user=request.user)
        return render(request, template_name='index.html', context={'score': score, 'status': status.status})
    return render(request, template_name='index.html',)


def top(request):

    ####
    # top_scores = (Score.objects.order_by('-score').values_list('score', flat=True).distinct())
    # users = Score.objects.order_by('-score').filter(score__in=top_scores[:10])
    kings = Status.objects.filter(status='KING').values('user')
    best_kings = Score.objects.order_by('-score').filter(user__in=kings)[:3]
    pros = Status.objects.filter(status='PRO').values('user')
    best_pros = Score.objects.order_by('-score').filter(user__in=pros)[:3]
    amateurs = Status.objects.filter(status='Amateur').values('user')
    best_amateurs = Score.objects.order_by('-score').filter(user__in=amateurs)[:3]
    ###

    if request.user.is_authenticated:
        if not Status.objects.filter(user=request.user).exists():
            Status.objects.create(user=request.user)
        status = Status.objects.get(user=request.user)
        users = Score.objects.order_by('-score')[:10]
        if not Score.objects.filter(user=request.user).exists():
            Score.objects.create(user=request.user)
        score = Score.objects.get(user=request.user)
        return render(request, template_name='top.html', context={'score': score, 'kings': best_kings, 'pros':best_pros, 'amateurs':best_amateurs,'status': status.status})
    return render(request, template_name='top.html', context={'kings': best_kings, 'pros':best_pros, 'amateurs':best_amateurs})


@login_required
def quiz(request):
    if not Status.objects.filter(user=request.user).exists():
        Status.objects.create(user=request.user)
    status = Status.objects.get(user=request.user)
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
                               'status': status.status
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
               'status': status.status,
               }

    return render(request, template_name='quiz.html', context=context)


@login_required
def quiz_multiple(request):
    if not Status.objects.filter(user=request.user).exists():
        Status.objects.create(user=request.user)
    status = Status.objects.get(user=request.user)
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
                               'status': status.status
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
               'status': status.status
               }

    return render(request, template_name='quiz_multiple.html', context=context)


@login_required
def upgrade(request):
    if not Status.objects.filter(user=request.user).exists():
        Status.objects.create(user=request.user)
    status = Status.objects.get(user=request.user)
    score = Score.objects.get(user=request.user)
    if request.method == 'POST':
        if status.status == 'beginner' and score.score >= 100:
            score.score -= 100
            status.status = 'Amateur'
            score.save()
            status.save()
            return redirect(reverse_lazy('app:upgrade'))
        if status.status == 'Amateur' and score.score >= 500:
            score.score -= 500
            status.status = 'PRO'
            score.save()
            status.save()
            return redirect(reverse_lazy('app:upgrade'))
        if status.status == 'PRO' and score.score >= 1000:
            score.score -= 1000
            status.status = 'KING'
            score.save()
            status.save()
            return redirect(reverse_lazy('app:upgrade'))
    if status.status == 'beginner' and  score.score >= 100:
        context = {
            'text': 'you can upgarde to AMATEUR (100 points)',
            'status': status.status,
            'score': score,
            'upgrade': True
            }
        return render(request, template_name='upgrade.html', context=context)
    if status.status == 'Amateur' and  score.score >= 500:
        context = {
        'text': 'you can upgarde to PRO (500 points)',
        'status': status.status,
        'score': score,
        'upgrade': True
        }
        return render(request, template_name='upgrade.html', context=context)
    if status.status == 'PRO' and  score.score >= 1000:
        context = {
        'text': 'you can upgarde to KING (1000 points)',
        'status': status.status,
        'score': score,
        'upgrade': True
        }
        
        return render(request, template_name='upgrade.html', context=context)
    if status.status == 'KING':
        context={
        'KING': True,
        'score': score,
        'status': status.status,
                }
        return render(request, template_name='upgrade.html', context=context)
    context={
        'text': 'not available<br>Amateur - 100 points<br>PRO - 500 points<br>KING - 1000 points',
        'score': score,
        'status': status.status,
    }
    return render(request, template_name='upgrade.html', context=context)