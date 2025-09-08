from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    """
    Customer/user testimonials
    """
    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('user', 'Product User'),
        ('student', 'Training Student'),
        ('partner', 'Business Partner'),
        ('employee', 'Employee'),
    ]

    # Personal information
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, help_text='Job title or role')
    company = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='testimonials/avatars/', blank=True, null=True)
    
    # Testimonial content
    content = models.TextField(help_text='The testimonial text')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    testimonial_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='customer')
    
    # Related product/service
    product_name = models.CharField(max_length=100, blank=True, help_text='Product or service being reviewed')
    
    # Social proof
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Display settings
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'testimonials'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_approved', 'is_featured']),
            models.Index(fields=['testimonial_type']),
        ]

    def __str__(self):
        return f"{self.name} - {self.company or 'Individual'}"

    @property
    def star_rating(self):
        """
        Return star rating as a list for template rendering
        """
        return list(range(self.rating))


class TestimonialSubmission(models.Model):
    """
    User-submitted testimonials (pending approval)
    """
    # Personal information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100, blank=True)
    
    # Testimonial content
    content = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    product_name = models.CharField(max_length=100, blank=True)
    
    # Contact information
    linkedin_url = models.URLField(blank=True, null=True)
    allow_contact = models.BooleanField(default=True, help_text='Allow Appnity to contact for follow-up')
    
    # Status
    is_approved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'testimonial_submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.name} ({'Approved' if self.is_approved else 'Pending'})"

    def approve_and_create_testimonial(self):
        """
        Approve submission and create public testimonial
        """
        if not self.is_approved:
            self.is_approved = True
            self.save()
            
            # Create public testimonial
            testimonial = Testimonial.objects.create(
                name=self.name,
                title=self.title,
                company=self.company,
                content=self.content,
                rating=self.rating,
                product_name=self.product_name,
                linkedin_url=self.linkedin_url,
                testimonial_type='customer',
                is_approved=True
            )
            
            return testimonial
        return None