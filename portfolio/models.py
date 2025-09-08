from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class PortfolioProject(models.Model):
    """
    Portfolio project model
    """
    CATEGORY_CHOICES = [
        ('web', 'Web Application'),
        ('mobile', 'Mobile Application'),
        ('saas', 'SaaS Platform'),
        ('api', 'API/Backend'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('maintenance', 'Maintenance'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    subtitle = models.CharField(max_length=200)
    description = MarkdownxField(help_text='Project description in Markdown')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Media
    featured_image = models.ImageField(upload_to='portfolio/images/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True, help_text='List of image URLs')
    
    # Links
    live_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    case_study_url = models.URLField(blank=True, null=True)
    
    # Project details
    client_name = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=50, help_text='e.g., "3 months", "6 weeks"')
    duration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text='Duration in weeks for filtering')
    team_size = models.PositiveIntegerField(default=1)
    
    # Metrics
    user_count = models.CharField(max_length=20, blank=True, help_text='e.g., "10K+", "500"')
    performance_metric = models.CharField(max_length=50, blank=True, help_text='e.g., "99.9% uptime"')
    business_impact = models.CharField(max_length=100, blank=True, help_text='e.g., "$1M+ revenue"')
    
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio_projects'
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


class ProjectTechnology(models.Model):
    """
    Technologies used in portfolio projects
    """
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='technologies')
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, help_text='e.g., Frontend, Backend, Database')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'portfolio_technologies'
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.project.title} - {self.name}"


class ProjectChallenge(models.Model):
    """
    Challenges faced during project development
    """
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=100)
    description = models.TextField()
    solution = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'portfolio_challenges'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ProjectResult(models.Model):
    """
    Project results and achievements
    """
    project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name='results')
    title = models.CharField(max_length=100)
    description = models.TextField()
    metric = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'portfolio_results'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"