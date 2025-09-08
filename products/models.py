from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Product(models.Model):
    """
    Product information model
    """
    STATUS_CHOICES = [
        ('live', 'Live'),
        ('beta', 'In Beta'),
        ('development', 'In Development'),
        ('coming_soon', 'Coming Soon'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    tagline = models.CharField(max_length=200, help_text='Short description/tagline')
    description = MarkdownxField(help_text='Detailed product description in Markdown')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    featured_image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    logo = models.ImageField(upload_to='products/logos/', blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    # Metrics
    user_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def description_html(self):
        return markdownify(self.description)


class ProductFeature(models.Model):
    """
    Product features
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_features'
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.title}"


class ProductTechnology(models.Model):
    """
    Technologies used in products
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='technologies')
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, help_text='e.g., Frontend, Backend, Database')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_technologies'
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductMetric(models.Model):
    """
    Product metrics and statistics
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'product_metrics'
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"