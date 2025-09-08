from rest_framework import serializers
from .models import NewsletterSubscription


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter subscription
    """
    class Meta:
        model = NewsletterSubscription
        fields = ['email']

    def create(self, validated_data):
        # Add IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Handle existing subscription
        email = validated_data['email']
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults=validated_data
        )
        
        if not created and not subscription.is_active:
            # Reactivate subscription
            subscription.resubscribe()
        
        return subscription

    def get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    """
    Serializer for newsletter unsubscription
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            subscription = NewsletterSubscription.objects.get(email=value, is_active=True)
        except NewsletterSubscription.DoesNotExist:
            raise serializers.ValidationError("Email not found in our newsletter list")
        return value


class NewsletterAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin newsletter management
    """
    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'email', 'is_active', 'source', 'ip_address', 
            'user_agent', 'subscribed_at', 'unsubscribed_at'
        ]
        read_only_fields = ['id', 'subscribed_at', 'unsubscribed_at']