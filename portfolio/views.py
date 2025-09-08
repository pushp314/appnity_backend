from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import PortfolioProject, ProjectTechnology
from .serializers import PortfolioProjectListSerializer, PortfolioProjectDetailSerializer
from .filters import PortfolioProjectFilter


class PortfolioProjectListView(generics.ListAPIView):
    """
    List all portfolio projects
    """
    queryset = PortfolioProject.objects.prefetch_related('technologies', 'challenges', 'results')
    serializer_class = PortfolioProjectListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PortfolioProjectFilter
    ordering = ['order', '-created_at']

    @extend_schema(
        summary="List portfolio projects",
        description="Get list of all portfolio projects with filtering options",
        parameters=[
            OpenApiParameter(name='category', description='Filter by project category'),
            OpenApiParameter(name='status', description='Filter by project status'),
            OpenApiParameter(name='is_featured', description='Filter featured projects'),
        ],
        responses={200: PortfolioProjectListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PortfolioProjectDetailView(generics.RetrieveAPIView):
    """
    Retrieve a portfolio project
    """
    queryset = PortfolioProject.objects.prefetch_related('technologies', 'challenges', 'results')
    serializer_class = PortfolioProjectDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @extend_schema(
        summary="Get portfolio project",
        description="Retrieve a single portfolio project by slug",
        responses={
            200: PortfolioProjectDetailSerializer,
            404: OpenApiResponse(description="Portfolio project not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    summary="Get featured projects",
    description="Retrieve featured portfolio projects",
    responses={200: PortfolioProjectListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_projects_view(request):
    """
    Get featured portfolio projects
    """
    featured_projects = PortfolioProject.objects.filter(
        is_featured=True
    ).prefetch_related('technologies', 'challenges', 'results')[:6]
    
    serializer = PortfolioProjectListSerializer(featured_projects, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get projects by category",
    description="Retrieve portfolio projects filtered by category",
    parameters=[
        OpenApiParameter(name='category', description='Project category', required=True),
    ],
    responses={200: PortfolioProjectListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def projects_by_category_view(request, category):
    """
    Get portfolio projects by category
    """
    projects = PortfolioProject.objects.filter(
        category=category
    ).prefetch_related('technologies', 'challenges', 'results')
    
    serializer = PortfolioProjectListSerializer(projects, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get project technologies",
    description="Get all unique technologies used across portfolio projects",
    responses={200: OpenApiResponse(description="List of technologies")}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def project_technologies_view(request):
    """
    Get all unique technologies used in portfolio projects
    """
    from django.db.models import Count
    
    technologies = ProjectTechnology.objects.values('name', 'category').annotate(
        project_count=Count('project', distinct=True)
    ).order_by('category', '-project_count')
    
    # Group by category
    tech_by_category = {}
    for tech in technologies:
        category = tech['category']
        if category not in tech_by_category:
            tech_by_category[category] = []
        tech_by_category[category].append({
            'name': tech['name'],
            'project_count': tech['project_count']
        })
    
    return Response(tech_by_category)


@extend_schema(
    summary="Search portfolio projects",
    description="Search portfolio projects by title, description, or technologies",
    parameters=[
        OpenApiParameter(name='q', description='Search query', required=True),
        OpenApiParameter(name='category', description='Filter by category'),
    ],
    responses={200: PortfolioProjectListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_projects_view(request):
    """
    Search portfolio projects
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    if not query:
        return Response({'error': 'Search query is required'}, status=400)
    
    # Build search queryset
    queryset = PortfolioProject.objects.prefetch_related('technologies', 'challenges', 'results')
    
    # Filter by category if provided
    if category:
        queryset = queryset.filter(category=category)
    
    # Search in title, subtitle, description, and technologies
    queryset = queryset.filter(
        models.Q(title__icontains=query) |
        models.Q(subtitle__icontains=query) |
        models.Q(description__icontains=query) |
        models.Q(technologies__name__icontains=query) |
        models.Q(client_name__icontains=query)
    ).distinct()
    
    serializer = PortfolioProjectListSerializer(queryset, many=True)
    return Response({
        'query': query,
        'category': category,
        'count': len(serializer.data),
        'results': serializer.data
    })