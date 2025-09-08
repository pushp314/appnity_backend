from rest_framework import serializers
from .models import Testimonial, TestimonialSubmission


class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer for testimonials
    """
    star_rating = serializers.ReadOnlyField()

    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'title', 'company', 'avatar', 'content',
            'rating', 'star_rating', 'testimonial_type', 'product_name',
            'linkedin_url', 'twitter_url', 'website_url', 'is_featured',
            'created_at', 'updated_at'
        ]


class TestimonialCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating testimonials (admin only)
    """
    class Meta:
        model = Testimonial
        fields = [
            'name', 'title', 'company', 'avatar', 'content', 'rating',
            'testimonial_type', 'product_name', 'linkedin_url', 'twitter_url',
            'website_url', 'is_featured', 'is_approved', 'order'
        ]


class TestimonialSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for testimonial submissions
    """
    class Meta:
        model = TestimonialSubmission
        fields = [
            'name', 'email', 'title', 'company', 'content', 'rating',
            'product_name', 'linkedin_url', 'allow_contact'
        ]

    def validate_content(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("Testimonial must be at least 20 characters long")
        return value.strip()

    def create(self, validated_data):
        # Add IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return TestimonialSubmission.objects.create(**validated_data)

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


class TestimonialSubmissionAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin testimonial submission management
    """
    class Meta:
        model = TestimonialSubmission
        fields = [
            'id', 'name', 'email', 'title', 'company', 'content', 'rating',
            'product_name', 'linkedin_url', 'allow_contact', 'is_approved',
            'admin_notes', 'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'name', 'email', 'title', 'company', 'content', 'rating',
            'product_name', 'linkedin_url', 'allow_contact', 'ip_address',
            'user_agent', 'created_at'
        ]