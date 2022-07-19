from django.urls import path
from app.views import index, quiz, top, quiz_multiple, upgrade


app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('quiz/', quiz, name='quiz'),
    path('quiz_multiple/', quiz_multiple, name='quiz_multiple'),
    path('top/', top, name='top'),
    path('upgrade/', upgrade, name='upgrade'),
]
