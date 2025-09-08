from django.contrib import admin
from .models import Testimonial, TestimonialSubmission


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'testimonial_type', 'rating', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['testimonial_type', 'rating', 'is_featured', 'is_approved', 'created_at']
    search_fields = ['name', 'company', 'content', 'product_name']
    actions = ['mark_as_featured', 'mark_as_not_featured', 'approve_testimonials']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'title', 'company', 'avatar')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'testimonial_type', 'product_name')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'twitter_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_approved', 'order')
        }),
    )

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = 'Mark selected testimonials as featured'

    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
    mark_as_not_featured.short_description = 'Remove featured status'

    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = 'Approve selected testimonials'


@admin.register(TestimonialSubmission)
class TestimonialSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'rating', 'product_name', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'allow_contact', 'created_at']
    search_fields = ['name', 'email', 'company', 'content', 'product_name']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    actions = ['approve_and_create_testimonials', 'approve_submissions', 'reject_submissions']
    
    fieldsets = (
        ('Submitter Information', {
            'fields': ('name', 'email', 'title', 'company')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'product_name')
        }),
        ('Contact Information', {
            'fields': ('linkedin_url', 'allow_contact')
        }),
        ('Review Status', {
            'fields': ('is_approved', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def approve_and_create_testimonials(self, request, queryset):
        count = 0
        for submission in queryset.filter(is_approved=False):
            testimonial = submission.approve_and_create_testimonial()
            if testimonial:
                count += 1
        
        self.message_user(request, f"Approved {count} testimonials and created public entries")
    approve_and_create_testimonials.short_description = 'Approve and create public testimonials'

    def approve_submissions(self, request, queryset):
        queryset.update(is_approved=True)
    approve_submissions.short_description = 'Approve selected submissions'

    def reject_submissions(self, request, queryset):
        queryset.update(is_approved=False)
    reject_submissions.short_description = 'Reject selected submissions'