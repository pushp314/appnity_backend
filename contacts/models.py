from django.db import models
from django.core.validators import EmailValidator


class Contact(models.Model):
    """
    Contact form submissions
    """
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('product', 'Product Support'),
        ('partnership', 'Partnership'),
        ('career', 'Career Opportunity'),
        ('press', 'Press & Media'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, help_text='Internal notes for admin use')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['inquiry_type']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_inquiry_type_display()}"

    @property
    def is_new(self):
        return self.status == 'new'


class Newsletter(models.Model):
    """
    Newsletter subscriptions
    """
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'newsletter_subscriptions'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

    def unsubscribe(self):
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()