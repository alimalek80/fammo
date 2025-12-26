from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from markdownx.models import MarkdownxField

# Get language choices from settings
LANGUAGE_CHOICES = getattr(settings, 'LANGUAGES', [('en', 'English')])

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  # Allow blank for auto-generation
    category = models.ManyToManyField(BlogCategory, null=True, blank=True, related_name='posts')
    content = MarkdownxField()  # stores markdown text; safe to keep existing data
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)  # AI-generated posts start as drafts
    published_at = models.DateTimeField(null=True, blank=True)
    meta_description = models.CharField(max_length=255, blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')

    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / ratings.count(), 2) if ratings.exists() else None

    @property
    def excerpt(self):
        """Compatible excerpt attribute backed by meta_description or a content snippet."""
        if self.meta_description:
            return self.meta_description
        return (self.content or "")[:200]

    @excerpt.setter
    def excerpt(self, value):
        self.meta_description = value

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class BlogRating(models.Model):
    post = models.ForeignKey(BlogPost, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('post', 'user')


# AI Blog Pipeline Models

class BlogTopic(models.Model):
    """
    Topic pool for AI blog generation. Admin maintains this list.
    """
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SKIPPED', 'Skipped'),
    ]

    title = models.CharField(max_length=200, unique=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    primary_keyword = models.CharField(max_length=100, blank=True)
    secondary_keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    target_audience = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text="Additional instructions for AI generation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.IntegerField(default=0, help_text="Higher priority topics are picked first")
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'created_at']
        verbose_name = 'Blog Topic'
        verbose_name_plural = 'Blog Topics'

    def __str__(self):
        return f"{self.title} ({self.language}) - {self.status}"


class BlogGenerationRequest(models.Model):
    """
    Tracks each AI generation request and stores the results.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATED', 'Generated'),
        ('FAILED', 'Failed'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
    ]
    
    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('friendly', 'Friendly'),
        ('authoritative', 'Authoritative'),
    ]

    topic = models.ForeignKey(BlogTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='generation_requests')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Generation results
    generated_json = models.JSONField(null=True, blank=True, help_text="Full JSON response from AI")
    blog_post = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True, blank=True, related_name='generation_request')
    
    # Social media drafts
    linkedin_draft = models.TextField(blank=True, help_text="LinkedIn post draft (600-1200 chars)")
    x_draft = models.TextField(blank=True, help_text="X/Twitter post draft (<=280 chars)")
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Generation Request'
        verbose_name_plural = 'Blog Generation Requests'

    def __str__(self):
        topic_str = self.topic.title if self.topic else "Manual Request"
        return f"Request #{self.id} - {topic_str} - {self.status}"


class BlogPostImageSuggestion(models.Model):
    """
    Image suggestions from AI for a blog post.
    """
    IMAGE_TYPE_CHOICES = [
        ('THUMBNAIL', 'Thumbnail'),
        ('INLINE', 'Inline'),
    ]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='image_suggestions')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    alt_text = models.CharField(max_length=200)
    prompt = models.TextField(help_text="AI image generation prompt")
    placement_hint = models.CharField(max_length=200, blank=True, help_text="Where to place the image in the post")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Blog Post Image Suggestion'
        verbose_name_plural = 'Blog Post Image Suggestions'

    def __str__(self):
        return f"{self.image_type} for {self.post.title}"

