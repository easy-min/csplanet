from django.contrib import admin

from .models import Exam, ExamQuestion, TestSession, UserAnswer, ExamResult

class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display       = ('id', 'title', 'start_datetime', 'end_datetime', 'created_by')
    filter_horizontal  = ('chapters',)
    inlines            = [ExamQuestionInline]

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exam', 'started_at', 'completed_at')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'question', 'selected_choice', 'is_correct', 'score')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('session', 'total_score', 'status', 'graded_at')