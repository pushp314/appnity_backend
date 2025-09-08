from django.contrib import admin
from .models import Contact, Newsletter


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'inquiry_type', 'status', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved', 'mark_as_in_progress']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'inquiry_type')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_as_resolved.short_description = 'Mark selected contacts as resolved'

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
    mark_as_in_progress.short_description = 'Mark selected contacts as in progress'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['ip_address', 'user_agent', 'subscribed_at', 'unsubscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)
    activate_subscriptions.short_description = 'Activate selected subscriptions'

    def deactivate_subscriptions(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'