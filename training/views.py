from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Course, Instructor
from .serializers import CourseListSerializer, CourseDetailSerializer, InstructorSerializer


class CourseListView(generics.ListAPIView):
    """
    List all courses
    """
    queryset = Course.objects.prefetch_related('modules', 'technologies', 'projects', 'course_instructors__instructor')
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'status', 'is_featured']
    ordering = ['order', '-created_at']

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


class CourseDetailView(generics.RetrieveAPIView):
    """
    Retrieve a course
    """
    queryset = Course.objects.prefetch_related(
        'modules', 'technologies', 'projects', 'course_instructors__instructor'
    )
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

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


class InstructorListView(generics.ListAPIView):
    """
    List all instructors
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List instructors",
        description="Get list of all course instructors",
        responses={200: InstructorSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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