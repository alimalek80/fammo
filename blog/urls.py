from django.urls import path
from . import views
from . import dashboard_views

app_name = 'blog'

urlpatterns = [
    # Dashboard routes (staff only) - MUST come before slug patterns
    path('dashboard/', dashboard_views.blog_dashboard, name='dashboard'),
    path('dashboard/topics/', dashboard_views.manage_topics, name='manage_topics'),
    path('dashboard/topics/create/', dashboard_views.create_topic, name='create_topic'),
    path('dashboard/topics/<int:topic_id>/edit/', dashboard_views.edit_topic, name='edit_topic'),
    path('dashboard/topics/<int:topic_id>/delete/', dashboard_views.delete_topic, name='delete_topic'),
    path('dashboard/topics/<int:topic_id>/generate/', dashboard_views.generate_from_topic, name='generate_from_topic'),
    path('dashboard/requests/', dashboard_views.my_generation_requests, name='my_generation_requests'),
    path('dashboard/requests/<int:request_id>/', dashboard_views.generation_request_detail, name='generation_request_detail'),
    path('dashboard/posts/', dashboard_views.my_blog_posts, name='my_blog_posts'),
    path('dashboard/generate/', dashboard_views.generate_blog, name='generate_blog'),
    path('dashboard/posts/<int:post_id>/publish/', dashboard_views.publish_blog_post, name='publish_post'),
    path('dashboard/posts/<int:post_id>/unpublish/', dashboard_views.unpublish_blog_post, name='unpublish_post'),
    path('dashboard/posts/<int:post_id>/delete/', dashboard_views.delete_blog_post, name='delete_post'),
    path('dashboard/uploads/inline-image/', dashboard_views.upload_inline_image, name='upload_inline_image'),
    
    # Public blog routes - slug patterns come last
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('<slug:slug>/rate/', views.rate_post, name='rate_post'),
    path('<slug:slug>/comment/', views.comment_post, name='comment_post'),
]