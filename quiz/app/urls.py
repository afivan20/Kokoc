from django.urls import path
from app.views import index, quiz, top


app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('quiz/', quiz, name='quiz'),
    path('top/', top, name='top'),
]