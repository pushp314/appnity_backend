from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Testimonial, TestimonialSubmission
from .serializers import (
    TestimonialSerializer,
    TestimonialCreateUpdateSerializer,
    TestimonialSubmissionSerializer,
    TestimonialSubmissionAdminSerializer
)


class TestimonialListView(generics.ListCreateAPIView):
    """
    List all testimonials or create new testimonial (admin only)
    """
    queryset = Testimonial.objects.filter(is_approved=True)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['testimonial_type', 'rating', 'is_featured']
    ordering = ['order', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TestimonialCreateUpdateSerializer
        return TestimonialSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Create testimonial",
        description="Create a new testimonial (admin only)",
        request=TestimonialCreateUpdateSerializer,
        responses={
            201: TestimonialSerializer,
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


class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a testimonial
    """
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TestimonialCreateUpdateSerializer
        return TestimonialSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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
            
            # Send confirmation email to submitter
            self.send_confirmation_email(submission)
            
            # Send notification email to admin
            self.send_admin_notification(submission)
            
            return Response({
                'message': 'Thank you for your testimonial! We\'ll review it and publish it soon.',
                'submission_id': submission.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_email(self, submission):
        """
        Send confirmation email to testimonial submitter
        """
        try:
            subject = 'Thank you for your testimonial!'
            message = f"""
Dear {submission.name},

Thank you for taking the time to share your experience with Appnity Software Private Limited!

Your testimonial has been submitted and is currently under review. We'll publish it on our website soon.

Testimonial Details:
- Product/Service: {submission.product_name or 'General'}
- Rating: {submission.rating}/5 stars

We truly appreciate your feedback and support.

Best regards,
The Appnity Team

---
Appnity Software Private Limited
Building developer-first digital products
https://appnity.co.in
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[submission.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")

    def send_admin_notification(self, submission):
        """
        Send notification email to admin about new testimonial
        """
        try:
            subject = f'New Testimonial Submission - {submission.rating}/5 stars'
            message = f"""
New testimonial submission received:

Name: {submission.name}
Email: {submission.email}
Title: {submission.title}
Company: {submission.company}
Product: {submission.product_name or 'General'}
Rating: {submission.rating}/5 stars

Testimonial:
{submission.content}

LinkedIn: {submission.linkedin_url}
Allow Contact: {submission.allow_contact}

Submitted at: {submission.created_at}
IP Address: {submission.ip_address}

Please review and approve in the admin panel.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send admin notification email: {e}")


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


@extend_schema(
    summary="Get testimonial statistics",
    description="Get testimonial statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Testimonial statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def testimonial_stats_view(request):
    """
    Get testimonial statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count, Avg

    stats = {
        'total_testimonials': Testimonial.objects.filter(is_approved=True).count(),
        'pending_submissions': TestimonialSubmission.objects.filter(is_approved=False).count(),
        'average_rating': Testimonial.objects.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0,
        'by_type': dict(
            Testimonial.objects.filter(is_approved=True)
            .values('testimonial_type')
            .annotate(count=Count('id'))
            .values_list('testimonial_type', 'count')
        ),
        'by_rating': dict(
            Testimonial.objects.filter(is_approved=True)
            .values('rating')
            .annotate(count=Count('id'))
            .values_list('rating', 'count')
        ),
        'featured_count': Testimonial.objects.filter(
            is_approved=True, is_featured=True
        ).count(),
    }

    return Response(stats)