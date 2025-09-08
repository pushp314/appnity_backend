from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import PortfolioProject, ProjectTechnology, ProjectChallenge, ProjectResult
from .serializers import (
    PortfolioProjectListSerializer,
    PortfolioProjectDetailSerializer,
    PortfolioProjectCreateUpdateSerializer
)
from .filters import PortfolioProjectFilter


class PortfolioProjectListView(generics.ListCreateAPIView):
    """
    List all portfolio projects or create new project (admin only)
    """
    queryset = PortfolioProject.objects.prefetch_related('technologies', 'challenges', 'results')
    filter_backends = [DjangoFilterBackend]
    filterset_class = PortfolioProjectFilter
    ordering = ['order', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PortfolioProjectCreateUpdateSerializer
        return PortfolioProjectListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Create portfolio project",
        description="Create a new portfolio project (admin only)",
        request=PortfolioProjectCreateUpdateSerializer,
        responses={
            201: PortfolioProjectDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
        }
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class PortfolioProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a portfolio project
    """
    queryset = PortfolioProject.objects.prefetch_related('technologies', 'challenges', 'results')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PortfolioProjectCreateUpdateSerializer
        return PortfolioProjectDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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
        summary="Update portfolio project",
        description="Update a portfolio project (admin only)",
        request=PortfolioProjectCreateUpdateSerializer,
        responses={
            200: PortfolioProjectDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Portfolio project not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete portfolio project",
        description="Delete a portfolio project (admin only)",
        responses={
            204: OpenApiResponse(description="Portfolio project deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Portfolio project not found"),
        }
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


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
    summary="Get portfolio statistics",
    description="Get portfolio project statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Portfolio statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def portfolio_stats_view(request):
    """
    Get portfolio statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count, Avg
    from django.utils import timezone
    from datetime import timedelta

    stats = {
        'total_projects': PortfolioProject.objects.count(),
        'completed_projects': PortfolioProject.objects.filter(status='completed').count(),
        'featured_projects': PortfolioProject.objects.filter(is_featured=True).count(),
        'by_category': dict(
            PortfolioProject.objects.values('category').annotate(
                count=Count('id')
            ).values_list('category', 'count')
        ),
        'by_status': dict(
            PortfolioProject.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        ),
        'total_technologies': ProjectTechnology.objects.values('name').distinct().count(),
        'most_used_technologies': list(
            ProjectTechnology.objects.values('name').annotate(
                count=Count('id')
            ).order_by('-count')[:10].values_list('name', 'count')
        ),
        'average_team_size': PortfolioProject.objects.aggregate(
            avg=Avg('team_size')
        )['avg'] or 0,
    }

    return Response(stats)


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
        return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
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