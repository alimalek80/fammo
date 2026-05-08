from django import forms
from markdownx.widgets import MarkdownxWidget
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'content', 'category', 'image', 'image_alt',
            'author', 'meta_description', 'meta_keywords',
            'seo_title', 'canonical_url', 'og_image',
        ]
        widgets = {
            'content': MarkdownxWidget()  # ensures editor + uploads on front-end forms
        }
        help_texts = {
            'image_alt': 'Describe the thumbnail image for accessibility (e.g., "Golden retriever puppy playing with a ball")',
            'content': 'Use Markdown syntax. For images in content, use: ![describe the image here](image-url)',
            'seo_title': 'Custom Google title (max 60 chars). Leave blank to use the post title.',
            'canonical_url': 'Paste the preferred URL if this content exists at multiple addresses.',
            'og_image': 'Social sharing image (Facebook, Twitter). Leave blank to use the main thumbnail.',
        }