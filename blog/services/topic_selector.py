"""
Topic selection logic for AI Blog Pipeline.
Ensures race-condition-safe topic selection using database locking.
"""
from django.db import transaction
from django.utils import timezone
from blog.models import BlogTopic


def pick_next_topic(language):
    """
    Selects the next TODO topic for the given language and marks it IN_PROGRESS.
    
    Uses select_for_update() to prevent race conditions when multiple 
    generation requests happen simultaneously.
    
    Args:
        language: Language code ('en', 'tr', 'fi')
    
    Returns:
        BlogTopic instance with status changed to IN_PROGRESS, or None if no topics available
    
    Raises:
        BlogTopic.DoesNotExist: If no TODO topics exist for the language
    """
    with transaction.atomic():
        # Lock the row to prevent concurrent access
        topic = (
            BlogTopic.objects
            .select_for_update()
            .filter(language=language, status='TODO')
            .order_by('-priority', 'created_at')
            .first()
        )
        
        if topic:
            topic.status = 'IN_PROGRESS'
            topic.last_used_at = timezone.now()
            topic.save(update_fields=['status', 'last_used_at', 'updated_at'])
        
        return topic


def mark_topic_in_progress(topic):
    """
    Marks a topic as IN_PROGRESS when generation starts.
    
    Args:
        topic: BlogTopic instance
    """
    topic.status = 'IN_PROGRESS'
    topic.last_used_at = timezone.now()
    topic.save(update_fields=['status', 'last_used_at', 'updated_at'])


def mark_topic_completed(topic):
    """
    Marks a topic as COMPLETED after successful generation.
    
    Args:
        topic: BlogTopic instance
    """
    topic.status = 'COMPLETED'
    topic.save(update_fields=['status', 'updated_at'])


def revert_topic_to_todo(topic):
    """
    Reverts a topic back to TODO status if generation fails.
    This allows retry on the next generation attempt.
    
    Args:
        topic: BlogTopic instance
    """
    topic.status = 'TODO'
    topic.last_used_at = None
    topic.save(update_fields=['status', 'last_used_at', 'updated_at'])
