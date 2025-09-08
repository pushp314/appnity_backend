from rest_framework import serializers
from .models import PortfolioProject, ProjectTechnology, ProjectChallenge, ProjectResult


class ProjectTechnologySerializer(serializers.ModelSerializer):
    """
    Serializer for project technologies
    """
    class Meta:
        model = ProjectTechnology
        fields = ['id', 'name', 'category', 'order']


class ProjectChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for project challenges
    """
    class Meta:
        model = ProjectChallenge
        fields = ['id', 'title', 'description', 'solution', 'order']


class ProjectResultSerializer(serializers.ModelSerializer):
    """
    Serializer for project results
    """
    class Meta:
        model = ProjectResult
        fields = ['id', 'title', 'description', 'metric', 'order']


class PortfolioProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer for portfolio project list view
    """
    technologies_count = serializers.SerializerMethodField()
    challenges_count = serializers.SerializerMethodField()
    results_count = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'slug', 'subtitle', 'category', 'status',
            'featured_image', 'client_name', 'duration', 'team_size',
            'duration_weeks',
            'user_count', 'performance_metric', 'business_impact',
            'is_featured', 'technologies_count', 'challenges_count',
            'results_count', 'created_at', 'updated_at'
        ]

    def get_technologies_count(self, obj):
        return obj.technologies.count()

    def get_challenges_count(self, obj):
        return obj.challenges.count()

    def get_results_count(self, obj):
        return obj.results.count()


class PortfolioProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for portfolio project detail view
    """
    description_html = serializers.ReadOnlyField()
    technologies = ProjectTechnologySerializer(many=True, read_only=True)
    challenges = ProjectChallengeSerializer(many=True, read_only=True)
    results = ProjectResultSerializer(many=True, read_only=True)

    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'title', 'slug', 'subtitle', 'description', 'description_html',
            'category', 'status', 'featured_image', 'gallery_images',
            'live_url', 'github_url', 'case_study_url', 'client_name',
            'duration', 'duration_weeks', 'team_size', 'user_count', 'performance_metric',
            'business_impact', 'is_featured', 'technologies', 'challenges',
            'results', 'created_at', 'updated_at'
        ]


class PortfolioProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating portfolio projects (admin only)
    """
    class Meta:
        model = PortfolioProject
        fields = [
            'title', 'subtitle', 'description', 'category', 'status',
            'featured_image', 'gallery_images', 'live_url', 'github_url',
            'case_study_url', 'client_name', 'duration', 'team_size',
            'duration_weeks',
            'user_count', 'performance_metric', 'business_impact',
            'is_featured', 'order'
        ]