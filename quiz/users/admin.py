from django.contrib import admin
from users.models import Score, Question


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question',)


admin.site.register(Score, ScoreAdmin)
admin.site.register(Question, QuestionAdmin)
