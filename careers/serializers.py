from rest_framework import serializers
from .models import JobPosition, JobSkill, JobApplication


class JobSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for job skills
    """
    class Meta:
        model = JobSkill
        fields = ['id', 'name', 'skill_type', 'experience_years', 'order']


class JobPositionListSerializer(serializers.ModelSerializer):
    """
    Serializer for job position list view
    """
    salary_range = serializers.ReadOnlyField()
    skills_count = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'slug', 'department', 'job_type', 'level',
            'location', 'salary_range', 'equity_offered', 'status',
            'is_featured', 'skills_count', 'applications_count',
            'application_deadline', 'created_at', 'updated_at'
        ]

    def get_skills_count(self, obj):
        return obj.skills.count()

    def get_applications_count(self, obj):
        return obj.applications.count()


class JobPositionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for job position detail view
    """
    description_html = serializers.ReadOnlyField()
    requirements_html = serializers.ReadOnlyField()
    responsibilities_html = serializers.ReadOnlyField()
    benefits_html = serializers.ReadOnlyField()
    salary_range = serializers.ReadOnlyField()
    skills = JobSkillSerializer(many=True, read_only=True)

    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'slug', 'department', 'job_type', 'level',
            'location', 'description', 'description_html', 'requirements',
            'requirements_html', 'responsibilities', 'responsibilities_html',
            'benefits', 'benefits_html', 'salary_min', 'salary_max',
            'salary_range', 'salary_currency', 'equity_offered',
            'application_deadline', 'application_email', 'application_url',
            'status', 'is_featured', 'skills', 'created_at', 'updated_at'
        ]


class JobPositionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating job positions (admin only)
    """
    class Meta:
        model = JobPosition
        fields = [
            'title', 'department', 'job_type', 'level', 'location',
            'description', 'requirements', 'responsibilities', 'benefits',
            'salary_min', 'salary_max', 'salary_currency', 'equity_offered',
            'application_deadline', 'application_email', 'application_url',
            'status', 'is_featured', 'order'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for job applications
    """
    class Meta:
        model = JobApplication
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'location',
            'cover_letter', 'resume', 'portfolio_url', 'github_url',
            'linkedin_url', 'years_of_experience', 'current_salary',
            'expected_salary'
        ]

    def validate_resume(self, value):
        # Validate file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume file size cannot exceed 5MB")
        
        # Validate file type
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Resume must be a PDF or Word document")
        
        return value

    def create(self, validated_data):
        # Add IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Add position from URL
        validated_data['position'] = self.context['position']
        
        return JobApplication.objects.create(**validated_data)

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


class JobApplicationAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin job application management
    """
    full_name = serializers.ReadOnlyField()
    position_title = serializers.CharField(source='position.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'position_title', 'full_name', 'first_name', 'last_name',
            'email', 'phone', 'location', 'cover_letter', 'resume',
            'portfolio_url', 'github_url', 'linkedin_url', 'years_of_experience',
            'current_salary', 'expected_salary', 'status', 'admin_notes',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'position_title', 'full_name', 'first_name', 'last_name',
            'email', 'phone', 'location', 'cover_letter', 'resume',
            'portfolio_url', 'github_url', 'linkedin_url', 'years_of_experience',
            'current_salary', 'expected_salary', 'ip_address', 'user_agent',
            'created_at'
        ]