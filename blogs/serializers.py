from rest_framework import serializers
from .models import BlogPost, Category, Tag, Comment
from users.serializers import UserPublicSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for blog categories
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color']


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for blog tags
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for blog comments
    """
    author = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []


class BlogPostListSerializer(serializers.ModelSerializer):
    """
    Serializer for blog post list view (minimal data)
    """
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 'author',
            'category', 'tags', 'is_featured', 'read_time', 'views_count',
            'comments_count', 'created_at', 'updated_at', 'published_at'
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for blog post detail view (full data)
    """
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    content_html = serializers.ReadOnlyField()
    comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'content_html',
            'featured_image', 'author', 'category', 'tags', 'is_featured',
            'read_time', 'views_count', 'comments', 'comments_count',
            'created_at', 'updated_at', 'published_at'
        ]

    def get_comments(self, obj):
        # Only return top-level comments (replies are nested)
        top_level_comments = obj.comments.filter(
            parent=None, 
            is_approved=True
        ).order_by('created_at')
        return CommentSerializer(top_level_comments, many=True).data

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating blog posts (admin only)
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        required=False
    )

    class Meta:
        model = BlogPost
        fields = [
            'title', 'excerpt', 'content', 'featured_image', 'category',
            'tags', 'status', 'is_featured', 'read_time'
        ]

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        blog_post = BlogPost.objects.create(**validated_data)
        blog_post.tags.set(tags)
        return blog_post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.set(tags)
        
        return instance


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments
    """
    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['post'] = self.context['post']
        return Comment.objects.create(**validated_data)