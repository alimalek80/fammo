from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Question(models.Model):
    """Pet-related questions from users"""
    
    title = models.CharField(max_length=200, help_text="Clear, descriptive question title")
    body = models.TextField(help_text="Detailed description of the issue")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    is_answered = models.BooleanField(default=False)
    
    # Tags for categorization
    CATEGORY_CHOICES = [
        ('dog_health', 'Dog Health'),
        ('cat_health', 'Cat Health'),
        ('dog_behavior', 'Dog Behavior'),
        ('cat_behavior', 'Cat Behavior'),
        ('nutrition', 'Nutrition & Diet'),
        ('training', 'Training'),
        ('grooming', 'Grooming'),
        ('veterinary', 'Veterinary Care'),
        ('adoption', 'Adoption & Rescue'),
        ('general', 'General'),
    ]
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='general'
    )
    
    # Generic relation for votes
    votes = GenericRelation('Vote', related_query_name='question')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum:question_detail', kwargs={'pk': self.pk})
    
    def get_vote_count(self):
        """Calculate net votes for this question"""
        upvotes = self.votes.filter(vote_type='up').count()
        downvotes = self.votes.filter(vote_type='down').count()
        return upvotes - downvotes
    
    def get_answer_count(self):
        """Get number of answers"""
        return self.answers.count()


class Answer(models.Model):
    """Answers to questions"""
    
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    body = models.TextField(help_text="Your answer or advice")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='answers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(
        default=False, 
        help_text="Marked as the best answer by question author"
    )
    
    # Generic relation for votes
    votes = GenericRelation('Vote', related_query_name='answer')
    
    class Meta:
        ordering = ['-is_accepted', '-created_at']
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
    
    def __str__(self):
        return f"Answer by {self.author.username} to: {self.question.title[:50]}"
    
    def get_vote_count(self):
        """Calculate net votes for this answer"""
        upvotes = self.votes.filter(vote_type='up').count()
        downvotes = self.votes.filter(vote_type='down').count()
        return upvotes - downvotes


class Vote(models.Model):
    """Upvote/downvote system for questions and answers"""
    
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='forum_votes'
    )
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Generic relation to vote on either Question or Answer
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.vote_type}"
