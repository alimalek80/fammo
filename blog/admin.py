from django.contrib import admin
from .models import BlogPost, BlogComment, BlogRating, BlogCategory

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "category", "author", "created_at")
    list_filter = ("category", "author")
    search_fields = ("title", "content")
    fields = (
        "title", "slug", "category", "content", "image", "author",
        "meta_description", "meta_keywords"
    )

admin.site.register(BlogComment)
admin.site.register(BlogRating)
