import re
from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost, BlogComment, BlogRating, BlogCategory
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from urllib.parse import quote
from django.utils.html import strip_tags
from django.utils import timezone


def _extract_faq_items(content):
    """Parse ## FAQ / ## Frequently Asked Questions section from markdown."""
    faq_section = re.search(
        r'^#{1,3}\s+(?:FAQ|Frequently Asked Questions?|Common Questions?)[^\n]*\n+(.*?)(?=\n#{1,2}\s|\Z)',
        content,
        re.IGNORECASE | re.DOTALL | re.MULTILINE,
    )
    if not faq_section:
        return []
    faq_body = faq_section.group(1)
    items = []
    for m in re.finditer(r'^#{2,4}\s+(.+?)\n+(.*?)(?=\n#{2,4}\s|\Z)', faq_body, re.DOTALL | re.MULTILINE):
        question = m.group(1).strip()
        answer = re.sub(r'\s+', ' ', strip_tags(m.group(2))).strip()
        if question and answer:
            items.append({'question': question, 'answer': answer})
    return items

SORT_OPTIONS = {
    'newest':   '-published_at',
    'oldest':   'published_at',
    'views':    '-views',
    'comments': '-comment_count',
    'rating':   '-avg_rating',
}

def blog_list(request):
    categories = BlogCategory.objects.all()
    selected_slug = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'newest')
    if sort_by not in SORT_OPTIONS:
        sort_by = 'newest'

    posts = BlogPost.objects.filter(
        published_at__isnull=False,
        published_at__lte=timezone.now()
    )

    if selected_slug:
        posts = posts.filter(category__slug=selected_slug)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__email__icontains=search_query) |
            Q(author__profile__first_name__icontains=search_query) |
            Q(author__profile__last_name__icontains=search_query)
        ).distinct()

    if sort_by in ('comments', 'rating'):
        if sort_by == 'comments':
            posts = posts.annotate(comment_count=Count('comments')).order_by('-comment_count')
        else:
            posts = posts.annotate(avg_rating=Avg('ratings__value')).order_by('-avg_rating')
    else:
        posts = posts.order_by(SORT_OPTIONS[sort_by])

    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/blog_list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_slug': selected_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    })

def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost,
        slug=slug,
        published_at__isnull=False,
        published_at__lte=timezone.now()
    )

    # Increment views
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
    post.refresh_from_db(fields=['views'])

    absolute_url = request.build_absolute_uri(request.path)
    image_url = request.build_absolute_uri(post.image.url) if getattr(post, "image", None) else ""

    # og_image takes priority for social sharing; falls back to the main thumbnail
    if post.og_image:
        og_image_url = request.build_absolute_uri(post.og_image.url)
    else:
        og_image_url = image_url

    # canonical_url: prefer the explicitly-set field, otherwise use the current page URL
    canonical_url_final = post.canonical_url or absolute_url

    # Previous and next posts (by created_at)
    prev_post = BlogPost.objects.filter(created_at__lt=post.created_at).order_by('-created_at').first()
    next_post = BlogPost.objects.filter(created_at__gt=post.created_at).order_by('created_at').first()


    # short description (match template truncation length if you want)
    share_desc = post.meta_description or strip_tags(post.content)[:200]

    # build plain text with real newlines, then URL-encode once
    share_text = f"{post.title}\n\n{share_desc}\n\n{absolute_url}"
    if image_url:
        share_text += f"\n\n{image_url}"

    share_text_encoded = quote(share_text)  # safe for inserting directly into href

    # Author display name for schema
    author_name = ''
    if post.author:
        try:
            p = post.author.profile
            author_name = f"{p.first_name} {p.last_name}".strip()
        except Exception:
            pass
        if not author_name and post.author.email:
            author_name = post.author.email

    faq_items = _extract_faq_items(post.content)

    user_rating = None
    if request.user.is_authenticated:
        user_rating = BlogRating.objects.filter(post=post, user=request.user).first()

    agg = post.ratings.aggregate(avg=Avg('value'), cnt=Count('id'))
    avg_rating = agg['avg'] or 0
    rating_count = agg['cnt'] or 0
    avg_rounded = int(round(avg_rating))

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'avg_rounded': avg_rounded,
        'rating_count': rating_count,
        'absolute_url': absolute_url,
        'image_url': image_url,
        'og_image_url': og_image_url,
        'canonical_url_final': canonical_url_final,
        'share_text_encoded': share_text_encoded,
        'prev_post': prev_post,
        'next_post': next_post,
        'author_name': author_name,
        'faq_items': faq_items,
    })

@login_required
def rate_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    value = int(request.POST.get('rating', 0))
    if 1 <= value <= 5:
        BlogRating.objects.update_or_create(post=post, user=request.user, defaults={'value': value})
    return redirect('blog:blog_detail', slug=slug)

@login_required
def comment_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    content = request.POST.get('content', '').strip()
    if content:
        BlogComment.objects.create(post=post, user=request.user, content=content)
    return redirect('blog:blog_detail', slug=slug)
