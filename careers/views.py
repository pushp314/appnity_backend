from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import JobPosition, JobApplication
from .serializers import (
    JobPositionListSerializer,
    JobPositionDetailSerializer,
    JobPositionCreateUpdateSerializer,
    JobApplicationSerializer,
    JobApplicationAdminSerializer
)


class JobPositionListView(generics.ListCreateAPIView):
    """
    List all job positions or create new position (admin only)
    """
    queryset = JobPosition.objects.prefetch_related('skills')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'job_type', 'level', 'status', 'is_featured']
    ordering = ['order', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobPositionCreateUpdateSerializer
        return JobPositionListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Create job position",
        description="Create a new job position (admin only)",
        request=JobPositionCreateUpdateSerializer,
        responses={
            201: JobPositionDetailSerializer,
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


class JobPositionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job position
    """
    queryset = JobPosition.objects.prefetch_related('skills')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return JobPositionCreateUpdateSerializer
        return JobPositionDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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

    @extend_schema(
        summary="Update job position",
        description="Update a job position (admin only)",
        request=JobPositionCreateUpdateSerializer,
        responses={
            200: JobPositionDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Job position not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)


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
            
            # Send confirmation email to applicant
            self.send_confirmation_email(application)
            
            # Send notification email to admin
            self.send_admin_notification(application)
            
            return Response({
                'message': 'Application submitted successfully! We\'ll review it and get back to you soon.',
                'application_id': application.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_email(self, application):
        """
        Send confirmation email to applicant
        """
        try:
            subject = f'Application Received - {application.position.title}'
            message = f"""
Dear {application.first_name},

Thank you for your interest in the {application.position.title} position at Appnity Software Private Limited!

We have received your application and our team will review it carefully. We'll get back to you within 5-7 business days with next steps.

Position Details:
- Title: {application.position.title}
- Department: {application.position.department}
- Type: {application.position.get_job_type_display()}
- Location: {application.position.location}

If you have any questions, feel free to reach out to us at careers@appnity.co.in

Best regards,
The Appnity Careers Team

---
Appnity Software Private Limited
Building developer-first digital products
https://appnity.co.in
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")

    def send_admin_notification(self, application):
        """
        Send notification email to admin about new application
        """
        try:
            subject = f'New Job Application - {application.position.title}'
            message = f"""
New job application received:

Position: {application.position.title}
Applicant: {application.full_name}
Email: {application.email}
Phone: {application.phone}
Location: {application.location}
Experience: {application.years_of_experience} years
Expected Salary: {application.expected_salary}

Portfolio: {application.portfolio_url}
GitHub: {application.github_url}
LinkedIn: {application.linkedin_url}

Cover Letter:
{application.cover_letter}

Submitted at: {application.created_at}
IP Address: {application.ip_address}

Please review the application in the admin panel.
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


class JobApplicationListView(generics.ListAPIView):
    """
    List job applications (admin only)
    """
    queryset = JobApplication.objects.select_related('position')
    serializer_class = JobApplicationAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'position', 'years_of_experience']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only allow admin users to view applications
        if not self.request.user.is_editor:
            return JobApplication.objects.none()
        return super().get_queryset()

    @extend_schema(
        summary="List job applications",
        description="Get list of job applications (admin only)",
        responses={
            200: JobApplicationAdminSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JobApplicationDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update job application (admin only)
    """
    queryset = JobApplication.objects.select_related('position')
    serializer_class = JobApplicationAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow admin users to view applications
        if not self.request.user.is_editor:
            return JobApplication.objects.none()
        return super().get_queryset()

    @extend_schema(
        summary="Get job application",
        description="Retrieve a specific job application (admin only)",
        responses={
            200: JobApplicationAdminSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Application not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update job application",
        description="Update application status and notes (admin only)",
        request=JobApplicationAdminSerializer,
        responses={
            200: JobApplicationAdminSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Application not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


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


@extend_schema(
    summary="Get career statistics",
    description="Get career and application statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Career statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def career_stats_view(request):
    """
    Get career statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count, Avg
    from django.utils import timezone
    from datetime import timedelta

    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    stats = {
        'total_positions': JobPosition.objects.count(),
        'open_positions': JobPosition.objects.filter(status='open').count(),
        'total_applications': JobApplication.objects.count(),
        'recent_applications': JobApplication.objects.filter(
            created_at__gte=thirty_days_ago
        ).count(),
        'by_status': dict(
            JobApplication.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        ),
        'by_department': dict(
            JobPosition.objects.values('department').annotate(
                count=Count('id')
            ).values_list('department', 'count')
        ),
        'average_experience': JobApplication.objects.aggregate(
            avg=Avg('years_of_experience')
        )['avg'] or 0,
    }

    return Response(stats)