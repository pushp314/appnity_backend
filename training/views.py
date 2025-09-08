from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Course, Instructor
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateUpdateSerializer,
    InstructorSerializer,
    InstructorCreateUpdateSerializer
)


class CourseListView(generics.ListCreateAPIView):
    """
    List all courses or create new course (admin only)
    """
    queryset = Course.objects.prefetch_related('modules', 'technologies', 'projects', 'course_instructors__instructor')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'status', 'is_featured']
    ordering = ['order', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(
        summary="List courses",
        description="Get list of all training courses with filtering options",
        parameters=[
            OpenApiParameter(name='level', description='Filter by course level'),
            OpenApiParameter(name='status', description='Filter by course status'),
            OpenApiParameter(name='is_featured', description='Filter featured courses'),
        ],
        responses={200: CourseListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create course",
        description="Create a new training course (admin only)",
        request=CourseCreateUpdateSerializer,
        responses={
            201: CourseDetailSerializer,
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


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a course
    """
    queryset = Course.objects.prefetch_related(
        'modules', 'technologies', 'projects', 'course_instructors__instructor'
    )
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(
        summary="Get course",
        description="Retrieve a single course by slug",
        responses={
            200: CourseDetailSerializer,
            404: OpenApiResponse(description="Course not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update course",
        description="Update a course (admin only)",
        request=CourseCreateUpdateSerializer,
        responses={
            200: CourseDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Course not found"),
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
        summary="Delete course",
        description="Delete a course (admin only)",
        responses={
            204: OpenApiResponse(description="Course deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Course not found"),
        }
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class InstructorListView(generics.ListCreateAPIView):
    """
    List all instructors or create new instructor (admin only)
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InstructorCreateUpdateSerializer
        return InstructorSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(
        summary="List instructors",
        description="Get list of all course instructors",
        responses={200: InstructorSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create instructor",
        description="Create a new instructor (admin only)",
        request=InstructorCreateUpdateSerializer,
        responses={
            201: InstructorSerializer,
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


@extend_schema(
    summary="Get featured courses",
    description="Retrieve featured training courses",
    responses={200: CourseListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_courses_view(request):
    """
    Get featured courses
    """
    featured_courses = Course.objects.filter(
        is_featured=True,
        status='active'
    ).prefetch_related('modules', 'technologies', 'projects')[:3]
    
    serializer = CourseListSerializer(featured_courses, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get course statistics",
    description="Get training course statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Course statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course_stats_view(request):
    """
    Get course statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count, Avg, Sum

    stats = {
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects.filter(status='active').count(),
        'total_students': Course.objects.aggregate(
            total=Sum('student_count')
        )['total'] or 0,
        'average_rating': Course.objects.aggregate(
            avg=Avg('rating')
        )['avg'] or 0,
        'by_level': dict(
            Course.objects.values('level').annotate(
                count=Count('id')
            ).values_list('level', 'count')
        ),
        'by_status': dict(
            Course.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        ),
        'total_instructors': Instructor.objects.count(),
    }

    return Response(stats)