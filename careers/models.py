from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class JobPosition(models.Model):
    """
    Job position model for careers page
    """
    TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]

    LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('principal', 'Principal'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('paused', 'Paused'),
        ('filled', 'Filled'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    department = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    location = models.CharField(max_length=100, default='Remote')
    
    # Job details
    description = MarkdownxField(help_text='Job description in Markdown')
    requirements = MarkdownxField(help_text='Job requirements in Markdown')
    responsibilities = MarkdownxField(help_text='Job responsibilities in Markdown')
    benefits = MarkdownxField(blank=True, help_text='Job benefits in Markdown')
    
    # Compensation
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    equity_offered = models.BooleanField(default=False)
    
    # Application details
    application_deadline = models.DateTimeField(null=True, blank=True)
    application_email = models.EmailField(blank=True)
    application_url = models.URLField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_positions'
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.department}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.department}"

    @property
    def description_html(self):
        return markdownify(self.description)

    @property
    def requirements_html(self):
        return markdownify(self.requirements)

    @property
    def responsibilities_html(self):
        return markdownify(self.responsibilities)

    @property
    def benefits_html(self):
        return markdownify(self.benefits) if self.benefits else ''

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+"
        return "Competitive"


class JobSkill(models.Model):
    """
    Skills required for job positions
    """
    SKILL_TYPES = [
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('nice_to_have', 'Nice to Have'),
    ]

    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES, default='required')
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'job_skills'
        ordering = ['skill_type', 'order']

    def __str__(self):
        return f"{self.position.title} - {self.name}"


class JobApplication(models.Model):
    """
    Job application submissions
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications')
    
    # Applicant information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Application details
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='applications/resumes/')
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Experience
    years_of_experience = models.PositiveIntegerField()
    current_salary = models.PositiveIntegerField(null=True, blank=True)
    expected_salary = models.PositiveIntegerField(null=True, blank=True)
    
    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    admin_notes = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_applications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['position', 'status']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"