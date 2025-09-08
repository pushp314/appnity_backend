from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Course(models.Model):
    """
    Training course model
    """
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('coming_soon', 'Coming Soon'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subtitle = models.CharField(max_length=300)
    description = MarkdownxField(help_text='Course description in Markdown')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Course details
    duration = models.CharField(max_length=50, help_text='e.g., "12 weeks", "40 hours"')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    preview_video_url = models.URLField(blank=True, null=True)
    
    # Metrics
    student_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_courses'
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def description_html(self):
        return markdownify(self.description)

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class CourseModule(models.Model):
    """
    Course modules/sections
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=50, help_text='e.g., "2 hours", "45 minutes"')

    class Meta:
        db_table = 'course_modules'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseTechnology(models.Model):
    """
    Technologies covered in courses
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='technologies')
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, help_text='e.g., Frontend, Backend, Database')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_technologies'
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.name}"


class CourseProject(models.Model):
    """
    Projects students will build in the course
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=Course.LEVEL_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_projects'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Instructor(models.Model):
    """
    Course instructors
    """
    name = models.CharField(max_length=100)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='instructors/avatars/', blank=True, null=True)
    title = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    
    # Social links
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instructors'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.title}"


class CourseInstructor(models.Model):
    """
    Many-to-many relationship between courses and instructors
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_instructors')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='instructor_courses')
    role = models.CharField(max_length=50, default='Lead Instructor')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'course_instructors'
        ordering = ['order']
        unique_together = ['course', 'instructor']

    def __str__(self):
        return f"{self.course.title} - {self.instructor.name}"