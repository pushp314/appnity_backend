from rest_framework import serializers
from .models import Course, CourseModule, CourseTechnology, CourseProject, Instructor, CourseInstructor


class InstructorSerializer(serializers.ModelSerializer):
    """
    Serializer for instructors
    """
    class Meta:
        model = Instructor
        fields = [
            'id', 'name', 'bio', 'avatar', 'title', 'experience_years',
            'linkedin_url', 'github_url', 'twitter_url', 'website_url'
        ]


class CourseInstructorSerializer(serializers.ModelSerializer):
    """
    Serializer for course instructors
    """
    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = CourseInstructor
        fields = ['instructor', 'role', 'order']


class CourseModuleSerializer(serializers.ModelSerializer):
    """
    Serializer for course modules
    """
    class Meta:
        model = CourseModule
        fields = ['id', 'title', 'description', 'duration', 'order']


class CourseTechnologySerializer(serializers.ModelSerializer):
    """
    Serializer for course technologies
    """
    class Meta:
        model = CourseTechnology
        fields = ['id', 'name', 'category', 'order']


class CourseProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for course projects
    """
    class Meta:
        model = CourseProject
        fields = ['id', 'title', 'description', 'difficulty', 'order']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for course list view
    """
    discount_percentage = serializers.ReadOnlyField()
    modules_count = serializers.SerializerMethodField()
    technologies_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'subtitle', 'level', 'status', 'duration',
            'price', 'original_price', 'discount_percentage', 'featured_image',
            'student_count', 'rating', 'completion_rate', 'is_featured',
            'modules_count', 'technologies_count', 'projects_count',
            'created_at', 'updated_at'
        ]

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_technologies_count(self, obj):
        return obj.technologies.count()

    def get_projects_count(self, obj):
        return obj.projects.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for course detail view
    """
    description_html = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    modules = CourseModuleSerializer(many=True, read_only=True)
    technologies = CourseTechnologySerializer(many=True, read_only=True)
    projects = CourseProjectSerializer(many=True, read_only=True)
    instructors = CourseInstructorSerializer(source='course_instructors', many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'subtitle', 'description', 'description_html',
            'level', 'status', 'duration', 'price', 'original_price',
            'discount_percentage', 'featured_image', 'preview_video_url',
            'student_count', 'rating', 'completion_rate', 'meta_description',
            'is_featured', 'modules', 'technologies', 'projects', 'instructors',
            'created_at', 'updated_at'
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating courses (admin only)
    """
    class Meta:
        model = Course
        fields = [
            'title', 'subtitle', 'description', 'level', 'status', 'duration',
            'price', 'original_price', 'featured_image', 'preview_video_url',
            'student_count', 'rating', 'completion_rate', 'meta_description',
            'is_featured', 'order'
        ]


class InstructorCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating instructors (admin only)
    """
    class Meta:
        model = Instructor
        fields = [
            'name', 'bio', 'avatar', 'title', 'experience_years',
            'linkedin_url', 'github_url', 'twitter_url', 'website_url'
        ]