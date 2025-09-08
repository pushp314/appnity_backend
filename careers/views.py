from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import JobPosition, JobApplication
from .serializers import JobPositionListSerializer, JobPositionDetailSerializer, JobApplicationSerializer


class JobPositionListView(generics.ListAPIView):
    """
    List all job positions
    """
    queryset = JobPosition.objects.prefetch_related('skills')
    serializer_class = JobPositionListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'job_type', 'level', 'status', 'is_featured']
    ordering = ['order', '-created_at']

    @extend_schema(
        summary="List job positions",
        description="Get list of all job positions with filtering options",
        parameters=[
            OpenApiParameter(name='department', description='Filter by department'),
            OpenApiParameter(name='job_type', description='Filter by job type'),
            OpenApiParameter(name='level', description='Filter by experience level'),
            OpenApiParameter(name='status', description='Filter by position status'),
            OpenApiParameter(name='is_featured', description='Filter featured positions'),
        ],
        responses={200: JobPositionListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JobPositionDetailView(generics.RetrieveAPIView):
    """
    Retrieve a job position
    """
    queryset = JobPosition.objects.prefetch_related('skills')
    serializer_class = JobPositionDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @extend_schema(
        summary="Get job position",
        description="Retrieve a single job position by slug",
        responses={
            200: JobPositionDetailSerializer,
            404: OpenApiResponse(description="Job position not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JobApplicationCreateView(generics.CreateAPIView):
    """
    Submit job application
    """
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Submit job application",
        description="Submit an application for a specific job position",
        request=JobApplicationSerializer,
        responses={
            201: OpenApiResponse(description="Application submitted successfully"),
            400: OpenApiResponse(description="Validation errors"),
            404: OpenApiResponse(description="Job position not found"),
        }
    )
    def post(self, request, position_slug):
        position = get_object_or_404(JobPosition, slug=position_slug, status='open')
        
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'position': position}
        )
        
        if serializer.is_valid():
            application = serializer.save()
            
            return Response({
                'message': 'Application submitted successfully! We\'ll review it and get back to you soon.',
                'application_id': application.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get open positions",
    description="Retrieve currently open job positions",
    responses={200: JobPositionListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def open_positions_view(request):
    """
    Get open job positions
    """
    open_positions = JobPosition.objects.filter(status='open').prefetch_related('skills')
    serializer = JobPositionListSerializer(open_positions, many=True)
    return Response(serializer.data)