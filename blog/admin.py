from django.contrib import admin
from .models import BlogPost, BlogComment, BlogRating, BlogCategory
from userapp.models import CustomUser
from markdownx.admin import MarkdownxModelAdmin

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")

@admin.register(BlogPost)
class BlogPostAdmin(MarkdownxModelAdmin):  # use MarkdownxModelAdmin for assets
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "category", "author", "created_at")
    list_filter = ("category", "author")
    search_fields = ("title", "content")
    fields = (
        "title", "slug", "category", "content", "image", "author",
        "meta_description", "meta_keywords"
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = CustomUser.objects.filter(
                is_staff=True
            ) | CustomUser.objects.filter(
                profile__is_writer=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(BlogComment)
admin.site.register(BlogRating)
