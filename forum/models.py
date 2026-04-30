import io
import os

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from PIL import Image


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

    # Optional pet photo attached to the question
    image = models.ImageField(
        upload_to='forum/questions/',
        blank=True,
        null=True,
        help_text='Optional photo (will be compressed to under 1 MB automatically)'
    )
    
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

    def _compress_image(self):
        """Compress self.image in-place to stay under 1 MB, preserving quality as much as possible."""
        MAX_BYTES = 1 * 1024 * 1024  # 1 MB
        MAX_DIMENSION = 1920

        img = Image.open(self.image)

        # Convert palette/RGBA to RGB for JPEG
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if too large, preserving aspect ratio
        if max(img.size) > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

        # Iteratively reduce quality until under 1 MB
        quality = 85
        output = io.BytesIO()
        while quality >= 40:
            output.seek(0)
            output.truncate(0)
            img.save(output, format='JPEG', quality=quality, optimize=True)
            if output.tell() <= MAX_BYTES:
                break
            quality -= 5

        # Use a clean filename with .jpg extension
        original_name = os.path.splitext(os.path.basename(self.image.name))[0]
        new_name = f"{original_name}.jpg"
        self.image.save(new_name, ContentFile(output.getvalue()), save=False)


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


# ── Signals for Question image management ──────────────────────────────────────

@receiver(pre_save, sender=Question)
def compress_and_delete_old_image(sender, instance, **kwargs):
    """Compress the newly uploaded image and delete the old one from disk."""
    if not instance.pk:
        # New question — just compress if an image was provided
        if instance.image:
            instance._compress_image()
        return

    try:
        old = Question.objects.get(pk=instance.pk)
    except Question.DoesNotExist:
        return

    old_image = old.image
    new_image = instance.image

    if new_image and new_image != old_image:
        # Compress the new upload
        instance._compress_image()
        # Delete the old file from disk
        if old_image:
            if os.path.isfile(old_image.path):
                os.remove(old_image.path)
    elif not new_image and old_image:
        # Image was cleared — delete old file
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


@receiver(post_delete, sender=Question)
def delete_image_on_question_delete(sender, instance, **kwargs):
    """Remove the image file from disk when a question is deleted."""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
