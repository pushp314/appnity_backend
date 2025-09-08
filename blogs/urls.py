from django.urls import path
from . import views

urlpatterns = [
    # Blog posts
    path('', views.BlogPostListView.as_view(), name='blog-list'),
    path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='blog-detail'),
    
    # Categories and tags
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    
    # Comments
    path('<slug:post_slug>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    
    # Special endpoints
    path('featured/', views.featured_posts_view, name='featured-posts'),
    path('recent/', views.recent_posts_view, name='recent-posts'),
]