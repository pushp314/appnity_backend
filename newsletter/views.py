from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import NewsletterSubscription
from .serializers import (
    NewsletterSubscriptionSerializer,
    NewsletterUnsubscribeSerializer,
    NewsletterAdminSerializer
)


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    Newsletter subscription endpoint
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Subscribe to newsletter",
        description="Subscribe to the Appnity newsletter for updates and insights",
        request=NewsletterSubscriptionSerializer,
        responses={
            201: OpenApiResponse(description="Successfully subscribed to newsletter"),
            400: OpenApiResponse(description="Validation errors or already subscribed"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            
            # Send welcome email
            self.send_welcome_email(subscription.email)
            
            return Response({
                'message': 'Successfully subscribed to newsletter! Welcome to the Appnity family! 🚀',
                'email': subscription.email
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_welcome_email(self, email):
        """
        Send welcome email to new subscriber
        """
        try:
            subject = 'Welcome to Appnity Newsletter! 🚀'
            message = f"""
Welcome to the Appnity family! 🚀

Thank you for subscribing to our newsletter. You'll receive:

📦 Product updates and new feature announcements
🔍 Behind-the-scenes content and development insights
🚀 Exclusive early access to new launches
📚 Technical articles and tutorials
💡 Industry insights and trends

We respect your privacy and won't spam you. You can unsubscribe at any time by replying to any of our emails.

Stay tuned for amazing content!

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
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")


class NewsletterListView(generics.ListAPIView):
    """
    List newsletter subscriptions (admin only)
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'source']
    ordering = ['-subscribed_at']

    def get_queryset(self):
        # Only allow admin users to view subscriptions
        if not self.request.user.is_editor:
            return NewsletterSubscription.objects.none()
        return super().get_queryset()

    @extend_schema(
        summary="List newsletter subscriptions",
        description="Get list of newsletter subscriptions (admin only)",
        responses={
            200: NewsletterAdminSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
            subscription = NewsletterSubscription.objects.get(email=email, is_active=True)
            subscription.unsubscribe()
            
            # Send confirmation email
            send_unsubscribe_confirmation(email)
            
            return Response({
                'message': 'Successfully unsubscribed from newsletter. We\'re sorry to see you go!'
            }, status=status.HTTP_200_OK)
        except NewsletterSubscription.DoesNotExist:
            return Response({
                'error': 'Email not found in our newsletter list'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get newsletter statistics",
    description="Get newsletter subscription statistics (admin only)",
    responses={
        200: OpenApiResponse(description="Newsletter statistics"),
        401: OpenApiResponse(description="Authentication required"),
        403: OpenApiResponse(description="Admin access required"),
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def newsletter_stats_view(request):
    """
    Get newsletter statistics (admin only)
    """
    if not request.user.is_editor:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    # Get stats for different time periods
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    stats = {
        'total_subscribers': NewsletterSubscription.objects.filter(is_active=True).count(),
        'total_unsubscribed': NewsletterSubscription.objects.filter(is_active=False).count(),
        'new_subscribers_30_days': NewsletterSubscription.objects.filter(
            subscribed_at__gte=thirty_days_ago,
            is_active=True
        ).count(),
        'new_subscribers_7_days': NewsletterSubscription.objects.filter(
            subscribed_at__gte=seven_days_ago,
            is_active=True
        ).count(),
        'by_source': dict(
            NewsletterSubscription.objects.filter(is_active=True)
            .values('source')
            .annotate(count=Count('id'))
            .values_list('source', 'count')
        ),
        'growth_trend': get_growth_trend(),
    }

    return Response(stats)


def send_unsubscribe_confirmation(email):
    """
    Send unsubscribe confirmation email
    """
    try:
        subject = 'You\'ve been unsubscribed from Appnity Newsletter'
        message = f"""
Hi there,

You have been successfully unsubscribed from the Appnity newsletter.

We're sorry to see you go! If you change your mind, you can always resubscribe at https://appnity.co.in

If you have any feedback about why you unsubscribed, we'd love to hear from you at hello@appnity.co.in

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
        print(f"Failed to send unsubscribe confirmation email: {e}")


def get_growth_trend():
    """
    Calculate newsletter growth trend for the last 7 days
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    growth_data = []
    
    for i in range(7):
        date = now - timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        subscriptions = NewsletterSubscription.objects.filter(
            subscribed_at__range=[start_of_day, end_of_day]
        ).count()
        
        unsubscriptions = NewsletterSubscription.objects.filter(
            unsubscribed_at__range=[start_of_day, end_of_day]
        ).count()
        
        growth_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'subscriptions': subscriptions,
            'unsubscriptions': unsubscriptions,
            'net_growth': subscriptions - unsubscriptions
        })
    
    return list(reversed(growth_data))