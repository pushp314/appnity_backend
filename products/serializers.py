from rest_framework import serializers
from .models import Product, ProductFeature, ProductTechnology, ProductMetric


class ProductFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for product features
    """
    class Meta:
        model = ProductFeature
        fields = ['id', 'title', 'description', 'icon', 'order']


class ProductTechnologySerializer(serializers.ModelSerializer):
    """
    Serializer for product technologies
    """
    class Meta:
        model = ProductTechnology
        fields = ['id', 'name', 'category', 'order']


class ProductMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for product metrics
    """
    class Meta:
        model = ProductMetric
        fields = ['id', 'name', 'value', 'description', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for product list view
    """
    features_count = serializers.SerializerMethodField()
    technologies_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'tagline', 'status', 'featured_image',
            'logo', 'is_featured', 'user_count', 'rating', 'features_count',
            'technologies_count', 'created_at', 'updated_at'
        ]

    def get_features_count(self, obj):
        return obj.features.count()

    def get_technologies_count(self, obj):
        return obj.technologies.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for product detail view
    """
    description_html = serializers.ReadOnlyField()
    features = ProductFeatureSerializer(many=True, read_only=True)
    technologies = ProductTechnologySerializer(many=True, read_only=True)
    metrics = ProductMetricSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'tagline', 'description', 'description_html',
            'status', 'featured_image', 'logo', 'website_url', 'github_url',
            'demo_url', 'is_featured', 'user_count', 'rating', 'features',
            'technologies', 'metrics', 'created_at', 'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products (admin only)
    """
    class Meta:
        model = Product
        fields = [
            'name', 'tagline', 'description', 'status', 'featured_image',
            'logo', 'website_url', 'github_url', 'demo_url', 'is_featured',
            'user_count', 'rating', 'order'
        ]