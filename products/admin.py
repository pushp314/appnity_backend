from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Product, ProductFeature, ProductTechnology, ProductMetric


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1
    fields = ['title', 'description', 'icon', 'order']


class ProductTechnologyInline(admin.TabularInline):
    model = ProductTechnology
    extra = 1
    fields = ['name', 'category', 'order']


class ProductMetricInline(admin.TabularInline):
    model = ProductMetric
    extra = 1
    fields = ['name', 'value', 'description', 'order']


@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):
    list_display = ['name', 'status', 'is_featured', 'user_count', 'rating', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['name', 'tagline', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductFeatureInline, ProductTechnologyInline, ProductMetricInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'tagline', 'description')
        }),
        ('Media', {
            'fields': ('featured_image', 'logo')
        }),
        ('Links', {
            'fields': ('website_url', 'github_url', 'demo_url')
        }),
        ('Status & Metrics', {
            'fields': ('status', 'is_featured', 'order', 'user_count', 'rating')
        }),
    )


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'order']
    list_filter = ['product']
    search_fields = ['title', 'description']


@admin.register(ProductTechnology)
class ProductTechnologyAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'category', 'order']
    list_filter = ['product', 'category']
    search_fields = ['name']


@admin.register(ProductMetric)
class ProductMetricAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'value', 'order']
    list_filter = ['product']
    search_fields = ['name', 'value']