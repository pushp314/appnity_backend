from rest_framework import serializers
from .models import Contact, Newsletter


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for contact form submissions
    """
    class Meta:
        model = Contact
        fields = ['name', 'email', 'inquiry_type', 'message']

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()

    def create(self, validated_data):
        # Add IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return Contact.objects.create(**validated_data)

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


class ContactAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin contact management
    """
    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'email', 'inquiry_type', 'message', 'status',
            'admin_notes', 'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'name', 'email', 'inquiry_type', 'message', 'ip_address', 'user_agent', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter subscriptions
    """
    class Meta:
        model = Newsletter
        fields = ['email']

    def create(self, validated_data):
        # Add IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Handle existing subscription
        email = validated_data['email']
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults=validated_data
        )
        
        if not created and not newsletter.is_active:
            # Reactivate subscription
            newsletter.is_active = True
            newsletter.unsubscribed_at = None
            newsletter.save()
        
        return newsletter

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
            newsletter = Newsletter.objects.get(email=value, is_active=True)
        except Newsletter.DoesNotExist:
            raise serializers.ValidationError("Email not found in our newsletter list")
        return value