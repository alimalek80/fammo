from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost, BlogComment, BlogRating
from django.contrib.auth.decorators import login_required

def blog_list(request):
    posts = BlogPost.objects.order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = BlogRating.objects.filter(post=post, user=request.user).first()
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'user_rating': user_rating,
    })

@login_required
def rate_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    value = int(request.POST.get('rating', 0))
    if 1 <= value <= 5:
        BlogRating.objects.update_or_create(post=post, user=request.user, defaults={'value': value})
    return redirect('blog_detail', slug=slug)

@login_required
def comment_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    content = request.POST.get('content', '').strip()
    if content:
        BlogComment.objects.create(post=post, user=request.user, content=content)
    return redirect('blog_detail', slug=slug)
