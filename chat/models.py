from django.db import models
from django.conf import settings
from django.utils import timezone
import os


def chat_image_path(instance, filename):
    """Generate path for chat images: chat_images/user_<id>/<date>/<filename>"""
    ext = filename.split('.')[-1]
    new_filename = f"{timezone.now().strftime('%H%M%S')}_{instance.id or 'temp'}.{ext}"
    return f"chat_images/user_{instance.session.user_id}/{timezone.now().strftime('%Y/%m/%d')}/{new_filename}"


class ChatSession(models.Model):
    """Groups chat messages for a user. A user can have multiple sessions."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    title = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat {self.id} - {self.user.email} - {self.created_at.strftime('%Y-%m-%d')}"

    def get_messages(self):
        return self.messages.all().order_by('created_at')

    def get_history_for_ai(self):
        """Get message history formatted for AI context."""
        messages = self.messages.all().order_by('created_at')
        history = []
        for msg in messages:
            history.append({
                'role': msg.role,
                'text': msg.text,
                'has_image': bool(msg.image)
            })
        return history


class ChatMessage(models.Model):
    """Individual chat message, either from user or bot."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField(blank=True, default="")
    image = models.ImageField(
        upload_to=chat_image_path,
        blank=True,
        null=True,
        help_text="Optional image uploaded by user"
    )
    # Store base64 temporarily for immediate AI processing (not persisted long-term)
    image_base64 = models.TextField(blank=True, null=True, help_text="Temporary base64 for AI processing")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{self.role}: {preview}"

    def save(self, *args, **kwargs):
        # Auto-generate session title from first user message
        if self.role == 'user' and self.session.title == "":
            title = self.text[:50] if self.text else "Image chat"
            self.session.title = title
            self.session.save(update_fields=['title'])
        super().save(*args, **kwargs)

    def delete_image_file(self):
        """Delete the image file from storage."""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
            self.image = None
            self.save(update_fields=['image'])

    @classmethod
    def cleanup_old_images(cls, days=7):
        """Delete images older than specified days to save storage."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_messages = cls.objects.filter(
            image__isnull=False,
            created_at__lt=cutoff_date
        ).exclude(image='')
        
        deleted_count = 0
        for msg in old_messages:
            try:
                if msg.image and os.path.isfile(msg.image.path):
                    os.remove(msg.image.path)
                    deleted_count += 1
                msg.image = None
                msg.image_base64 = None
                msg.save(update_fields=['image', 'image_base64'])
            except Exception:
                pass
        
        return deleted_count
