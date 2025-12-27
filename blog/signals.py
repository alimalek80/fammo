import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from blog.models import BlogPost
from blog.services.blog_index_generator import generate_blog_index
from blog.services.vector_store_manager import force_refresh_vector_store

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=BlogPost)
def track_previous_publish_state(sender, instance, **kwargs):
    """Capture publish state before save so we can detect first-time publishes."""
    if not instance.pk:
        instance._was_published = False
        return
    try:
        previous = BlogPost.objects.get(pk=instance.pk)
        instance._was_published = bool(previous.is_published)
    except BlogPost.DoesNotExist:
        instance._was_published = False


@receiver(post_save, sender=BlogPost)
def refresh_index_on_publish(sender, instance, created, **kwargs):
    """Refresh blog index/vector store when a post is (newly) published."""
    was_published = getattr(instance, "_was_published", False)
    if not instance.is_published or (not created and was_published):
        return
    try:
        generate_blog_index()
        force_refresh_vector_store()
        logger.info("Refreshed blog index and vector store after publish for slug=%s", instance.slug)
    except Exception as exc:
        logger.error("Failed to refresh vector store after publish for slug=%s: %s", instance.slug, exc)
