from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Testimonial, TestimonialSubmission
from .serializers import TestimonialSerializer, TestimonialSubmissionSerializer


class TestimonialListView(generics.ListAPIView):
    """
    List all testimonials
    """
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['testimonial_type', 'rating', 'is_featured']
    ordering = ['order', '-created_at']

    @extend_schema(
        summary="List testimonials",
        description="Get list of approved testimonials with filtering options",
        parameters=[
            OpenApiParameter(name='testimonial_type', description='Filter by testimonial type'),
            OpenApiParameter(name='rating', description='Filter by rating'),
            OpenApiParameter(name='is_featured', description='Filter featured testimonials'),
        ],
        responses={200: TestimonialSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TestimonialDetailView(generics.RetrieveAPIView):
    """
    Retrieve a testimonial
    """
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Get testimonial",
        description="Retrieve a single testimonial",
        responses={
            200: TestimonialSerializer,
            404: OpenApiResponse(description="Testimonial not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TestimonialSubmissionCreateView(generics.CreateAPIView):
    """
    Submit testimonial for approval
    """
    queryset = TestimonialSubmission.objects.all()
    serializer_class = TestimonialSubmissionSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Submit testimonial",
        description="Submit a testimonial for approval",
        request=TestimonialSubmissionSerializer,
        responses={
            201: OpenApiResponse(description="Testimonial submitted successfully"),
            400: OpenApiResponse(description="Validation errors"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save()
            
            return Response({
                'message': 'Thank you for your testimonial! We\'ll review it and publish it soon.',
                'submission_id': submission.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get featured testimonials",
    description="Retrieve featured testimonials",
    responses={200: TestimonialSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_testimonials_view(request):
    """
    Get featured testimonials
    """
    featured_testimonials = Testimonial.objects.filter(
        is_approved=True,
        is_featured=True
    )[:6]
    
    serializer = TestimonialSerializer(featured_testimonials, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get testimonials by type",
    description="Retrieve testimonials filtered by type",
    parameters=[
        OpenApiParameter(name='type', description='Testimonial type', required=True),
    ],
    responses={200: TestimonialSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def testimonials_by_type_view(request, testimonial_type):
    """
    Get testimonials by type
    """
    testimonials = Testimonial.objects.filter(
        is_approved=True,
        testimonial_type=testimonial_type
    )
    
    serializer = TestimonialSerializer(testimonials, many=True)
    return Response(serializer.data)