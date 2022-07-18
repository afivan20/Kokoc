from django.contrib import admin
from users.models import Score, Question, Status


class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question',)

class StatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'status',)

admin.site.register(Score, ScoreAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Status, StatusAdmin)
