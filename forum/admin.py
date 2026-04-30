from django.contrib import admin
from .models import Question, Answer, Vote


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_answered', 'views', 'created_at')
    list_filter = ('category', 'is_answered', 'created_at')
    search_fields = ('title', 'body', 'author__username')
    readonly_fields = ('views', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Question', {
            'fields': ('title', 'body', 'author', 'category')
        }),
        ('Status', {
            'fields': ('is_answered', 'views')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('get_question_title', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('body', 'author__username', 'question__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def get_question_title(self, obj):
        return obj.question.title[:50]
    get_question_title.short_description = 'Question'
    
    fieldsets = (
        ('Answer', {
            'fields': ('question', 'body', 'author', 'is_accepted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'vote_type', 'content_type', 'object_id', 'created_at')
    list_filter = ('vote_type', 'content_type', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
