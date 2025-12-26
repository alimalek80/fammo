"""
Blog Index Generator - Creates a JSON file of all published blog posts
for OpenAI file_search tool to access.
"""
import json
from pathlib import Path
from django.conf import settings
from blog.models import BlogPost


def generate_blog_index():
    """
    Generates a JSON file containing all published blog posts with their
    titles, slugs, descriptions, and language.
    
    Returns:
        Path to the generated JSON file
    """
    # Get all published blog posts
    published_posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-published_at').values(
        'title', 'slug', 'language', 'meta_description', 'published_at'
    )
    
    # Structure the data for AI consumption
    blog_index = {
        "metadata": {
            "description": "Index of all published blog posts on FAMMO",
            "total_posts": published_posts.count(),
            "last_updated": "auto-generated"
        },
        "posts": []
    }
    
    for post in published_posts:
        blog_index["posts"].append({
            "title": post['title'],
            "slug": post['slug'],
            "language": post['language'],
            "description": post['meta_description'] or "",
            "url": f"https://fammo.ai/blog/{post['slug']}",
            "published_date": post['published_at'].isoformat() if post['published_at'] else None
        })
    
    # Save to media directory
    output_dir = Path(settings.MEDIA_ROOT) / 'blog_index'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'published_blogs.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(blog_index, f, indent=2, ensure_ascii=False)
    
    return output_file


def get_blog_index_content():
    """
    Returns the blog index as a formatted string for inclusion in prompts.
    """
    output_file = Path(settings.MEDIA_ROOT) / 'blog_index' / 'published_blogs.json'
    
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    return "{}"
