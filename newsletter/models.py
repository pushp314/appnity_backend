from django.db import models
from django.core.validators import EmailValidator


class NewsletterSubscription(models.Model):
    """
    Newsletter subscription model
    """
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    source = models.CharField(max_length=50, default='website', help_text='Source of subscription')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'newsletter_subscriptions'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['subscribed_at']),
        ]

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"

    def unsubscribe(self):
        """
        Unsubscribe user from newsletter
        """
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])

    def resubscribe(self):
        """
        Resubscribe user to newsletter
        """
        self.is_active = True
        self.unsubscribed_at = None
        self.save(update_fields=['is_active', 'unsubscribed_at'])