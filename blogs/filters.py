import django_filters
from .models import BlogPost, Category, Tag


class BlogPostFilter(django_filters.FilterSet):
    """
    Filter for blog posts
    """
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    tags = django_filters.CharFilter(method='filter_tags')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='iexact')
    featured = django_filters.BooleanFilter(field_name='is_featured')
    date_from = django_filters.DateFilter(field_name='published_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='published_at', lookup_expr='lte')

    class Meta:
        model = BlogPost
        fields = ['category', 'tags', 'author', 'featured', 'date_from', 'date_to']

    def filter_tags(self, queryset, name, value):
        """
        Filter by multiple tags (comma-separated)
        """
        if value:
            tag_slugs = [tag.strip() for tag in value.split(',')]
            return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset