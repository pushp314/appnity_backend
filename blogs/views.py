from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import BlogPost, Category, Tag, Comment
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
)
from .filters import BlogPostFilter


class BlogPostListView(generics.ListAPIView):
    """
    List all published blog posts
    """
    queryset = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BlogPostFilter
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['created_at', 'published_at', 'views_count']
    ordering = ['-published_at']

    @extend_schema(
        summary="List blog posts",
        description="Get paginated list of published blog posts with filtering and search",
        parameters=[
            OpenApiParameter(name='category', description='Filter by category slug'),
            OpenApiParameter(name='tags', description='Filter by tag slugs (comma-separated)'),
            OpenApiParameter(name='search', description='Search in title, excerpt, and content'),
            OpenApiParameter(name='ordering', description='Order by: created_at, published_at, views_count'),
        ],
        responses={200: BlogPostListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BlogPostDetailView(generics.RetrieveAPIView):
    """
    Retrieve a blog post
    """
    queryset = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags', 'comments')
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @extend_schema(
        summary="Get blog post",
        description="Retrieve a single blog post by slug",
        responses={
            200: BlogPostDetailSerializer,
            404: OpenApiResponse(description="Blog post not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment view count
        if response.status_code == 200:
            blog_post = self.get_object()
            blog_post.increment_views()
        return response


class CategoryListView(generics.ListAPIView):
    """
    List all blog categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List categories",
        description="Get all blog categories",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TagListView(generics.ListAPIView):
    """
    List all blog tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List tags",
        description="Get all blog tags",
        responses={200: TagSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Get featured posts",
    description="Retrieve featured blog posts",
    responses={200: BlogPostListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_posts_view(request):
    """
    Get featured blog posts
    """
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True
    ).select_related('author', 'category').prefetch_related('tags')[:3]
    
    serializer = BlogPostListSerializer(featured_posts, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get recent posts",
    description="Retrieve most recent blog posts",
    parameters=[
        OpenApiParameter(name='limit', description='Number of posts to return (default: 5)', type=int),
    ],
    responses={200: BlogPostListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_posts_view(request):
    """
    Get recent blog posts
    """
    limit = int(request.GET.get('limit', 5))
    recent_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('author', 'category').prefetch_related('tags')[:limit]
    
    serializer = BlogPostListSerializer(recent_posts, many=True)
    return Response(serializer.data)