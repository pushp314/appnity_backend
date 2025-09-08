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
    BlogPostCreateUpdateSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
    CommentCreateSerializer
)
from .filters import BlogPostFilter
from .permissions import IsAuthorOrAdminOrReadOnly


class BlogPostListView(generics.ListCreateAPIView):
    """
    List all published blog posts or create new post (admin only)
    """
    queryset = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BlogPostFilter
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['created_at', 'published_at', 'views_count']
    ordering = ['-published_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BlogPostCreateUpdateSerializer
        return BlogPostListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAuthorOrAdminOrReadOnly()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Create blog post",
        description="Create a new blog post (admin/editor only)",
        request=BlogPostCreateUpdateSerializer,
        responses={
            201: BlogPostDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a blog post
    """
    lookup_field = 'slug'
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_editor:
            return BlogPost.objects.select_related('author', 'category').prefetch_related('tags', 'comments')
        return BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags', 'comments')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BlogPostCreateUpdateSerializer
        return BlogPostDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrAdminOrReadOnly()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Update blog post",
        description="Update a blog post (author or admin only)",
        request=BlogPostCreateUpdateSerializer,
        responses={
            200: BlogPostDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Blog post not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete blog post",
        description="Delete a blog post (author or admin only)",
        responses={
            204: OpenApiResponse(description="Blog post deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Blog post not found"),
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


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


class CommentListCreateView(generics.ListCreateAPIView):
    """
    List comments for a blog post or create new comment
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs['post_slug']
        return Comment.objects.filter(
            post__slug=post_slug,
            parent=None,  # Only top-level comments
            is_approved=True
        ).select_related('author').prefetch_related('replies')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    @extend_schema(
        summary="List comments",
        description="Get comments for a specific blog post",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create comment",
        description="Add a comment to a blog post",
        request=CommentCreateSerializer,
        responses={
            201: CommentSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Blog post not found"),
        }
    )
    def post(self, request, *args, **kwargs):
        post_slug = self.kwargs['post_slug']
        post = get_object_or_404(BlogPost, slug=post_slug, status='published')
        
        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request, 'post': post}
        )
        if serializer.is_valid():
            comment = serializer.save()
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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