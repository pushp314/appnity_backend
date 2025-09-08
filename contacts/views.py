from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Contact, Newsletter
from .serializers import (
    ContactSerializer,
    ContactAdminSerializer,
    NewsletterSerializer,
    NewsletterUnsubscribeSerializer
)


class ContactCreateView(generics.CreateAPIView):
    """
    Create contact form submission
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Submit contact form",
        description="Submit a contact form inquiry",
        request=ContactSerializer,
        responses={
            201: OpenApiResponse(description="Contact form submitted successfully"),
            400: OpenApiResponse(description="Validation errors"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            
            # Send notification email to admin
            self.send_notification_email(contact)
            
            return Response({
                'message': 'Thank you for your message. We\'ll get back to you soon!',
                'id': contact.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_notification_email(self, contact):
        """
        Send notification email to admin about new contact submission
        """
        try:
            subject = f'New Contact Form Submission - {contact.get_inquiry_type_display()}'
            message = f"""
New contact form submission received:

Name: {contact.name}
Email: {contact.email}
Inquiry Type: {contact.get_inquiry_type_display()}
Message: {contact.message}

Submitted at: {contact.created_at}
IP Address: {contact.ip_address}

Please respond to this inquiry promptly.
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to send notification email: {e}")


class ContactListView(generics.ListAPIView):
    """
    List contact submissions (admin only)
    """
    queryset = Contact.objects.all()
    serializer_class = ContactAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'inquiry_type']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only allow admin users to view contacts
        if not self.request.user.is_editor:
            return Contact.objects.none()
        return super().get_queryset()

    @extend_schema(
        summary="List contact submissions",
        description="Get list of contact form submissions (admin only)",
        responses={
            200: ContactAdminSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ContactDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update contact submission (admin only)
    """
    queryset = Contact.objects.all()
    serializer_class = ContactAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow admin users to view contacts
        if not self.request.user.is_editor:
            return Contact.objects.none()
        return super().get_queryset()

    @extend_schema(
        summary="Get contact submission",
        description="Retrieve a specific contact submission (admin only)",
        responses={
            200: ContactAdminSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Contact not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update contact submission",
        description="Update contact submission status and notes (admin only)",
        request=ContactAdminSerializer,
        responses={
            200: ContactAdminSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Contact not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    Newsletter subscription endpoint
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Subscribe to newsletter",
        description="Subscribe to the Appnity newsletter",
        request=NewsletterSerializer,
        responses={
            201: OpenApiResponse(description="Successfully subscribed to newsletter"),
            400: OpenApiResponse(description="Validation errors or already subscribed"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            newsletter = serializer.save()
            
            # Send welcome email
            self.send_welcome_email(newsletter.email)
            
            return Response({
                'message': 'Successfully subscribed to newsletter!',
                'email': newsletter.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_welcome_email(self, email):
        """
        Send welcome email to new subscriber
        """
        try:
            subject = 'Welcome to Appnity Newsletter!'
            message = f"""
Welcome to the Appnity family! 🚀

Thank you for subscribing to our newsletter. You'll receive:
- Product updates and new feature announcements
- Behind-the-scenes content and development insights
- Exclusive early access to new launches
- Technical articles and tutorials

We respect your privacy and won't spam you. You can unsubscribe at any time.

Best regards,
The Appnity Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")


@extend_schema(
    summary="Unsubscribe from newsletter",
    description="Unsubscribe an email from the newsletter",
    request=NewsletterUnsubscribeSerializer,
    responses={
        200: OpenApiResponse(description="Successfully unsubscribed"),
        400: OpenApiResponse(description="Email not found or validation errors"),
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def newsletter_unsubscribe_view(request):
    """
    Unsubscribe from newsletter
    """
    serializer = NewsletterUnsubscribeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            newsletter = Newsletter.objects.get(email=email, is_active=True)
            newsletter.unsubscribe()
            return Response({
                'message': 'Successfully unsubscribed from newsletter'
            }, status=status.HTTP_200_OK)
        except Newsletter.DoesNotExist:
            return Response({
                'error': 'Email not found in our newsletter list'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get contact statistics",
    description="Get contact form submission statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Contact statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def contact_stats_view(request):
    """
    Get contact form statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    # Get stats for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    stats = {
        'total_contacts': Contact.objects.count(),
        'new_contacts': Contact.objects.filter(status='new').count(),
        'recent_contacts': Contact.objects.filter(created_at__gte=thirty_days_ago).count(),
        'by_inquiry_type': dict(
            Contact.objects.values('inquiry_type').annotate(
                count=Count('id')
            ).values_list('inquiry_type', 'count')
        ),
        'by_status': dict(
            Contact.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        ),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
    }

    return Response(stats)