"""
Blog Generation Dashboard Views

This module provides a dashboard for writers and admins to manage their blog generation
requests and blog posts. Only staff users (writers and admins) can access this dashboard.
"""
import logging
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (LANGUAGE_CHOICES, BlogGenerationRequest, BlogPost,
                     BlogPostImageSuggestion, BlogTopic)
from .services.ai_blog_generator import generate_for_next_topic


def is_writer_or_admin(user):
    """Check if user is staff (writer) or admin."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def blog_dashboard(request):
    """
    Main dashboard view for blog generation.
    
    Shows:
    - Statistics (total posts, published, drafts, pending generations)
    - Recent blog generation requests
    - User's blog posts
    - Quick actions
    """
    user = request.user
    
    # Get statistics
    if user.is_superuser:
        # Admin sees all posts and requests
        all_posts = BlogPost.objects.all()
        all_requests = BlogGenerationRequest.objects.all()
    else:
        # Writers see only their own
        all_posts = BlogPost.objects.filter(author=user)
        all_requests = BlogGenerationRequest.objects.filter(created_by=user)
    
    stats = {
        'total_posts': all_posts.count(),
        'published_posts': all_posts.filter(is_published=True).count(),
        'draft_posts': all_posts.filter(is_published=False).count(),
        'total_requests': all_requests.count(),
        'pending_requests': all_requests.filter(status='PENDING').count(),
        'processing_requests': 0,  # No processing status in model
        'completed_requests': all_requests.filter(status='GENERATED').count(),
        'failed_requests': all_requests.filter(status='FAILED').count(),
    }
    
    # Recent generation requests (last 10)
    recent_requests = all_requests.order_by('-created_at')[:10]
    
    # Recent blog posts (last 10)
    recent_posts = all_posts.order_by('-created_at')[:10]
    
    # Separate requests by status for Kanban view
    pending_list = all_requests.filter(status='PENDING').order_by('-created_at')[:10]
    processing_list = []  # No processing status in model
    completed_list = all_requests.filter(status='GENERATED').order_by('-created_at')[:10]
    
    # Get available topics
    from django.conf import settings
    languages = settings.LANGUAGES
    
    context = {
        'stats': stats,
        'recent_requests': recent_requests,
        'recent_posts': recent_posts,
        'pending_list': pending_list,
        'processing_list': processing_list,
        'completed_list': completed_list,
        'languages': languages,
        'user': user,
    }
    
    return render(request, 'blog/dashboard.html', context)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def my_generation_requests(request):
    """
    View all generation requests for current user.
    
    Supports filtering by status and language.
    """
    user = request.user
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    language_filter = request.GET.get('language', '')
    
    # Base queryset
    if user.is_superuser:
        requests = BlogGenerationRequest.objects.all()
    else:
        requests = BlogGenerationRequest.objects.filter(created_by=user)
    
    # Apply filters
    if status_filter:
        requests = requests.filter(status=status_filter)
    if language_filter:
        requests = requests.filter(language=language_filter)
    
    requests = requests.select_related('topic', 'blog_post', 'created_by').order_by('-created_at')
    
    context = {
        'requests': requests,
        'status_filter': status_filter,
        'language_filter': language_filter,
        'status_choices': BlogGenerationRequest.STATUS_CHOICES,
        'language_choices': LANGUAGE_CHOICES,
    }
    
    return render(request, 'blog/generation_requests.html', context)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def my_blog_posts(request):
    """
    View all blog posts for current user.
    
    Supports filtering by publication status and language.
    """
    user = request.user
    
    # Get filter parameters
    published_filter = request.GET.get('published', '')
    language_filter = request.GET.get('language', '')
    
    # Base queryset
    if user.is_superuser:
        posts = BlogPost.objects.all()
    else:
        posts = BlogPost.objects.filter(author=user)
    
    # Apply filters
    if published_filter == 'yes':
        posts = posts.filter(is_published=True)
    elif published_filter == 'no':
        posts = posts.filter(is_published=False)
    
    if language_filter:
        posts = posts.filter(language=language_filter)
    
    posts = posts.order_by('-created_at')
    
    context = {
        'posts': posts,
        'published_filter': published_filter,
        'language_filter': language_filter,
    }
    
    return render(request, 'blog/my_posts.html', context)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def generation_request_detail(request, request_id):
    """
    View detailed information about a specific generation request.
    
    Shows:
    - Request metadata
    - Generated blog post (if created)
    - Image suggestions
    - Social media drafts
    - Full JSON response
    """
    user = request.user
    
    # Get request
    gen_request = get_object_or_404(BlogGenerationRequest, id=request_id)
    
    # Check permission (only owner or admin can view)
    if not user.is_superuser and gen_request.created_by != user:
        messages.error(request, "You don't have permission to view this request.")
        return redirect('blog:dashboard')
    
    # If POST, handle inline edit/save/publish
    if request.method == 'POST' and gen_request.blog_post:
        # Permission: only owner or admin can edit/publish
        if not user.is_superuser and gen_request.blog_post.author != user:
            messages.error(request, "You don't have permission to modify this post.")
            return redirect('blog:generation_request_detail', request_id=request_id)

        post = gen_request.blog_post
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.excerpt = request.POST.get('excerpt', post.excerpt)
        post.meta_description = request.POST.get('meta_description', post.meta_description)
        post.meta_keywords = request.POST.get('meta_keywords', post.meta_keywords)

        # Optional thumbnail upload
        thumbnail = request.FILES.get('thumbnail')
        if thumbnail:
            post.image = thumbnail

        action = request.POST.get('action')
        if action == 'publish':
            post.is_published = True
            if not post.published_at:
                post.published_at = timezone.now()
            messages.success(request, f'Post "{post.title}" published.')
        elif action == 'unpublish':
            post.is_published = False
            messages.success(request, f'Post "{post.title}" unpublished.')
        else:
            messages.success(request, f'Post "{post.title}" saved.')

        post.save()
        return redirect('blog:generation_request_detail', request_id=request_id)

    # Get related data
    image_suggestions = None
    if gen_request.blog_post:
        image_suggestions = BlogPostImageSuggestion.objects.filter(post=gen_request.blog_post)
    
    context = {
        'gen_request': gen_request,
        'image_suggestions': image_suggestions,
    }
    
    return render(request, 'blog/generation_request_detail.html', context)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def generate_blog(request):
    """
    Handle blog generation request from dashboard.
    
    POST parameters:
    - language: Language code (en, tr, fi)
    - tone: Tone of the blog (professional, casual, friendly, authoritative)
    """
    if request.method != 'POST':
        return redirect('blog:dashboard')
    
    language = request.POST.get('language', 'en')
    tone = request.POST.get('tone', 'professional')
    
    try:
        # Generate blog for next topic
        gen_request = generate_for_next_topic(
            language=language,
            tone=tone,
            created_by=request.user
        )
        
        messages.success(
            request,
            f'Blog generation completed successfully! Topic: "{gen_request.topic.title}"'
        )
        return redirect('blog:generation_request_detail', request_id=gen_request.id)
    except ValueError as e:
        messages.error(request, f'Generation failed: {str(e)}')
        return redirect('blog:dashboard')
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
        return redirect('blog:dashboard')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def generate_from_topic(request, topic_id):
    """
    Generate a blog from a specific topic.
    """
    if request.method != 'POST':
        return redirect('blog:manage_topics')
    
    topic = get_object_or_404(BlogTopic, id=topic_id)
    
    # Check if topic is already in progress or completed
    if topic.status != 'TODO':
        messages.warning(request, f'Topic "{topic.title}" is already {topic.status.lower()}.')
        return redirect('blog:manage_topics')
    
    try:
        from .services.ai_blog_generator import generate_blog_from_topic
        
        # Generate blog for this specific topic with default settings
        gen_request = generate_blog_from_topic(
            topic=topic,
            language=topic.language,
            tone='professional',  # Default tone
            created_by=request.user
        )
        
        messages.success(
            request,
            f'Blog generation started for "{topic.title}"! Check the request details.'
        )
        return redirect('blog:generation_request_detail', request_id=gen_request.id)
        
    except Exception as e:
        messages.error(request, f'Generation failed: {str(e)}')
        return redirect('blog:manage_topics')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def publish_blog_post(request, post_id):
    """
    Publish a blog post (set is_published=True and published_at=now).
    
    Only the author or admin can publish.
    """
    if request.method != 'POST':
        return redirect('blog:my_posts')
    
    user = request.user
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Check permission
    if not user.is_superuser and post.author != user:
        messages.error(request, "You don't have permission to publish this post.")
        return redirect('blog:my_posts')
    
    # Publish post
    post.is_published = True
    if not post.published_at:
        post.published_at = timezone.now()
    post.save()
    
    messages.success(request, f'Blog post "{post.title}" has been published!')
    
    # Redirect to post detail or back to list
    next_url = request.POST.get('next', 'blog:my_posts')
    return redirect(next_url)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def unpublish_blog_post(request, post_id):
    """
    Unpublish a blog post (set is_published=False).
    
    Only the author or admin can unpublish.
    """
    if request.method != 'POST':
        return redirect('blog:my_posts')
    
    user = request.user
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Check permission
    if not user.is_superuser and post.author != user:
        messages.error(request, "You don't have permission to unpublish this post.")
        return redirect('blog:my_posts')
    
    # Unpublish post
    post.is_published = False
    post.save()
    
    messages.success(request, f'Blog post "{post.title}" has been unpublished!')
    
    next_url = request.POST.get('next', 'blog:my_posts')
    return redirect(next_url)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def delete_blog_post(request, post_id):
    """
    Delete a blog post.
    
    Only the author or admin can delete.
    """
    if request.method != 'POST':
        return redirect('blog:my_posts')
    
    user = request.user
    post = get_object_or_404(BlogPost, id=post_id)
    
    # Check permission
    if not user.is_superuser and post.author != user:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('blog:my_posts')
    
    post_title = post.title
    post.delete()
    
    messages.success(request, f'Blog post "{post_title}" has been deleted!')
    return redirect('blog:my_blog_posts')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def manage_topics(request):
    """
    View and manage blog topics.
    Shows all available topics organized by status.
    """
    user = request.user
    
    # Get topics organized by status
    todo_topics = BlogTopic.objects.filter(status='TODO').order_by('-priority', 'created_at')
    in_progress_topics = BlogTopic.objects.filter(status='IN_PROGRESS').order_by('-last_used_at')
    completed_topics = BlogTopic.objects.filter(status='COMPLETED').order_by('-last_used_at')[:20]  # Limit completed
    
    context = {
        'todo_topics': todo_topics,
        'in_progress_topics': in_progress_topics,
        'completed_topics': completed_topics,
        'languages': settings.LANGUAGES,
        'user': user,
    }
    
    return render(request, 'blog/manage_topics.html', context)


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def create_topic(request):
    """
    Create a new blog topic.
    """
    if request.method != 'POST':
        return redirect('blog:manage_topics')
    
    # Get form data
    title = request.POST.get('title', '').strip()
    language = request.POST.get('language', 'en')
    primary_keyword = request.POST.get('primary_keyword', '').strip()
    secondary_keywords = request.POST.get('secondary_keywords', '').strip()
    target_audience = request.POST.get('target_audience', '').strip()
    notes = request.POST.get('notes', '').strip()
    priority = int(request.POST.get('priority', 0))
    
    # Validate
    if not title:
        messages.error(request, 'Topic title is required.')
        return redirect('blog:manage_topics')
    
    # Check for duplicates
    if BlogTopic.objects.filter(title__iexact=title).exists():
        messages.error(request, f'A topic with the title "{title}" already exists.')
        return redirect('blog:manage_topics')
    
    # Create topic
    try:
        topic = BlogTopic.objects.create(
            title=title,
            language=language,
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            target_audience=target_audience,
            notes=notes,
            priority=priority,
            status='TODO'
        )
        messages.success(request, f'Topic "{topic.title}" has been created successfully!')
    except Exception as e:
        messages.error(request, f'Error creating topic: {str(e)}')
    
    return redirect('blog:manage_topics')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def edit_topic(request, topic_id):
    """
    Edit an existing blog topic.
    """
    if request.method != 'POST':
        return redirect('blog:manage_topics')
    
    topic = get_object_or_404(BlogTopic, id=topic_id)
    
    # Get form data
    title = request.POST.get('title', '').strip()
    language = request.POST.get('language', 'en')
    primary_keyword = request.POST.get('primary_keyword', '').strip()
    secondary_keywords = request.POST.get('secondary_keywords', '').strip()
    target_audience = request.POST.get('target_audience', '').strip()
    notes = request.POST.get('notes', '').strip()
    priority = int(request.POST.get('priority', 0))
    
    # Validate
    if not title:
        messages.error(request, 'Topic title is required.')
        return redirect('blog:manage_topics')
    
    # Check for duplicates (excluding current topic)
    if BlogTopic.objects.filter(title__iexact=title).exclude(id=topic_id).exists():
        messages.error(request, f'A topic with the title "{title}" already exists.')
        return redirect('blog:manage_topics')
    
    # Update topic
    try:
        topic.title = title
        topic.language = language
        topic.primary_keyword = primary_keyword
        topic.secondary_keywords = secondary_keywords
        topic.target_audience = target_audience
        topic.notes = notes
        topic.priority = priority
        topic.save()
        messages.success(request, f'Topic "{topic.title}" has been updated successfully!')
    except Exception as e:
        messages.error(request, f'Error updating topic: {str(e)}')
    
    return redirect('blog:manage_topics')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def delete_topic(request, topic_id):
    """
    Delete a blog topic.
    """
    if request.method != 'POST':
        return redirect('blog:manage_topics')
    
    topic = get_object_or_404(BlogTopic, id=topic_id)
    
    # Check if topic is being used
    if BlogGenerationRequest.objects.filter(topic=topic).exists():
        messages.error(request, f'Cannot delete topic "{topic.title}" - it has associated generation requests.')
        return redirect('blog:manage_topics')
    
    topic_title = topic.title
    topic.delete()
    
    messages.success(request, f'Topic "{topic_title}" has been deleted.')
    return redirect('blog:manage_topics')


@login_required
@user_passes_test(is_writer_or_admin, login_url='/admin/login/')
def upload_inline_image(request):
    """Handle inline image uploads from the markdown editor."""
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    image_file = request.FILES['image']

    try:
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'blog_inline')
        os.makedirs(upload_dir, exist_ok=True)

        ext = os.path.splitext(image_file.name)[1] or '.png'
        filename = f"blog_inline/{uuid.uuid4().hex}{ext}"

        saved_path = default_storage.save(filename, image_file)
        image_url = request.build_absolute_uri(default_storage.url(saved_path))

        return JsonResponse({'url': image_url})
    except Exception as exc:
        logging.exception("Inline image upload failed")
        return JsonResponse({'error': str(exc)}, status=500)
