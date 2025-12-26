from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from django.shortcuts import redirect
from .models import (
    BlogPost, BlogComment, BlogRating, BlogCategory,
    BlogTopic, BlogGenerationRequest, BlogPostImageSuggestion
)
from .services import generate_for_next_topic
from userapp.models import CustomUser
from markdownx.admin import MarkdownxModelAdmin

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")

@admin.register(BlogPost)
class BlogPostAdmin(MarkdownxModelAdmin):  # use MarkdownxModelAdmin for assets
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "category_list", "author", "language", "is_published", "created_at", "published_at", "views")
    list_filter = ("category", "author", "language", "is_published")
    search_fields = ("title", "content")
    fields = (
        "title", "slug", "category", "content", "image", "author",
        "meta_description", "meta_keywords", "language", "is_published", "published_at"
    )
    filter_horizontal = ("category",)
    actions = ['publish_selected_posts']

    def category_list(self, obj):
        return ", ".join([c.name for c in obj.category.all()])
    category_list.short_description = "Category"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = CustomUser.objects.filter(
                is_staff=True
            ) | CustomUser.objects.filter(
                profile__is_writer=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def publish_selected_posts(self, request, queryset):
        """
        Admin action to publish selected blog posts.
        Sets is_published=True and published_at=now() for unpublished posts.
        """
        unpublished = queryset.filter(is_published=False)
        count = unpublished.count()
        
        for post in unpublished:
            post.is_published = True
            if not post.published_at:
                post.published_at = timezone.now()
            post.save()
        
        self.message_user(request, f"Successfully published {count} blog post(s).")
    
    publish_selected_posts.short_description = "Publish selected blog posts"

admin.site.register(BlogComment)
admin.site.register(BlogRating)


# AI Blog Pipeline Admin

@admin.register(BlogTopic)
class BlogTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'status', 'priority', 'last_used_at', 'created_at')
    list_filter = ('language', 'status')
    search_fields = ('title', 'primary_keyword', 'notes')
    fields = (
        'title', 'language', 'primary_keyword', 'secondary_keywords',
        'target_audience', 'notes', 'status', 'priority', 'last_used_at'
    )
    readonly_fields = ('last_used_at',)
    actions = ['reset_to_todo', 'mark_completed', 'mark_skipped']
    
    def reset_to_todo(self, request, queryset):
        """Reset selected topics to TODO status."""
        count = queryset.update(status='TODO', last_used_at=None)
        self.message_user(request, f"Reset {count} topic(s) to TODO status.")
    reset_to_todo.short_description = "Reset to TODO"
    
    def mark_completed(self, request, queryset):
        """Mark selected topics as COMPLETED."""
        count = queryset.update(status='COMPLETED')
        self.message_user(request, f"Marked {count} topic(s) as COMPLETED.")
    mark_completed.short_description = "Mark COMPLETED"
    
    def mark_skipped(self, request, queryset):
        """Mark selected topics as SKIPPED."""
        count = queryset.update(status='SKIPPED')
        self.message_user(request, f"Marked {count} topic(s) as SKIPPED.")
    mark_skipped.short_description = "Mark SKIPPED"


@admin.register(BlogGenerationRequest)
class BlogGenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_display', 'language', 'status', 'created_by', 'created_at', 'blog_post_link')
    list_filter = ('language', 'status', 'created_at')
    search_fields = ('topic__title', 'error_message')
    readonly_fields = ('generated_json', 'error_message', 'created_at', 'updated_at', 'blog_post_link')
    fields = (
        'topic', 'language', 'tone', 'status', 'blog_post_link',
        'linkedin_draft', 'x_draft', 'generated_json', 'error_message',
        'created_by', 'created_at', 'updated_at'
    )
    actions = ['generate_en_topic', 'generate_tr_topic', 'generate_fi_topic']
    
    def topic_display(self, obj):
        return obj.topic.title if obj.topic else "Manual Request"
    topic_display.short_description = "Topic"
    
    def blog_post_link(self, obj):
        """Display clickable link to the generated blog post."""
        if obj.blog_post:
            url = f"/admin/blog/blogpost/{obj.blog_post.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.blog_post.title)
        return "-"
    blog_post_link.short_description = "Blog Post"
    
    def generate_en_topic(self, request, queryset):
        """Generate blog draft for next English topic."""
        return self._generate_topic(request, 'en')
    generate_en_topic.short_description = "🤖 Generate Next English Topic"
    
    def generate_tr_topic(self, request, queryset):
        """Generate blog draft for next Turkish topic."""
        return self._generate_topic(request, 'tr')
    generate_tr_topic.short_description = "🤖 Generate Next Turkish Topic"
    
    def generate_fi_topic(self, request, queryset):
        """Generate blog draft for next Finnish topic."""
        return self._generate_topic(request, 'fi')
    generate_fi_topic.short_description = "🤖 Generate Next Finnish Topic"
    
    def _generate_topic(self, request, language):
        """Helper method to generate blog for a specific language."""
        try:
            generation_request = generate_for_next_topic(
                language=language,
                tone='professional',
                created_by=request.user
            )
            
            self.message_user(
                request,
                f"Successfully generated blog draft for topic: {generation_request.topic.title}. "
                f"Blog post: {generation_request.blog_post.title}",
                level=messages.SUCCESS
            )
            
            # Redirect to the generated request detail page
            return redirect(f'/admin/blog/bloggenerationrequest/{generation_request.id}/change/')
            
        except ValueError as e:
            self.message_user(
                request,
                f"No TODO topics available for language: {language}",
                level=messages.WARNING
            )
        except Exception as e:
            self.message_user(
                request,
                f"Generation failed: {str(e)}",
                level=messages.ERROR
            )


@admin.register(BlogPostImageSuggestion)
class BlogPostImageSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'image_type', 'alt_text', 'created_at')
    list_filter = ('image_type', 'created_at')
    search_fields = ('post__title', 'alt_text', 'prompt')
    readonly_fields = ('created_at',)
    fields = ('post', 'image_type', 'alt_text', 'prompt', 'placement_hint', 'created_at')

