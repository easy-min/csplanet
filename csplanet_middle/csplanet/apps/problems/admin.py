from django.contrib import admin
from .models.topic import Topic
from .models.chapter import Chapter
from .models.objective_problem import ObjectiveProblem, ObjectiveChoice
from .models.subjective_problem import SubjectiveProblem, QuestionKeywordMapping, SubjectiveKeyword

# Topic
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name')
    search_fields = ('name',)

# Chapter
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'topic')
    list_filter   = ('topic',)
    search_fields = ('name',)

# ObjectiveChoice Inline
class ObjectiveChoiceInline(admin.TabularInline):
    model = ObjectiveChoice
    extra = 0

# ObjectiveProblem
@admin.register(ObjectiveProblem)
class ObjectiveProblemAdmin(admin.ModelAdmin):
    list_display  = ('id', 'chapter', 'creator', 'created_at', 'content', 'score', 'explanation')
    list_filter   = ('chapter', 'creator')
    search_fields = ('content', 'creator_username', 'chapter_name')
    inlines       = [ObjectiveChoiceInline]

# ObjectiveChoice standalone
@admin.register(ObjectiveChoice)
class ObjectiveChoiceAdmin(admin.ModelAdmin):
    list_display  = ('id', 'question', 'content', 'is_correct')
    list_filter   = ('is_correct', 'question')
    search_fields = ('content',)

# QuestionKeywordMapping Inline
class QuestionKeywordInline(admin.TabularInline):
    model = QuestionKeywordMapping
    extra = 0

# SubjectiveProblem
@admin.register(SubjectiveProblem)
class SubjectiveProblemAdmin(admin.ModelAdmin):
    list_display  = ('id', 'chapter', 'creator', 'created_at')
    list_filter   = ('chapter', 'creator')
    search_fields = ('content',)
    inlines       = [QuestionKeywordInline]

# QuestionKeywordMapping standalone
@admin.register(QuestionKeywordMapping)
class QuestionKeywordMappingAdmin(admin.ModelAdmin):
    list_display  = ('id', 'question', 'keyword', 'importance')
    list_filter   = ('importance', 'keyword')
    search_fields = ('keyword__name',)

@admin.register(SubjectiveKeyword)
class SubjectiveKeywordAdmin(admin.ModelAdmin):
    list_display  = ('id', 'word', 'synonyms')
    search_fields = ('word',)