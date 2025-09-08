from django.contrib import admin
from .models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'source', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'source', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['ip_address', 'user_agent', 'subscribed_at', 'unsubscribed_at']
    date_hierarchy = 'subscribed_at'
    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    fieldsets = (
        ('Subscription Info', {
            'fields': ('email', 'is_active', 'source')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )

    def activate_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.resubscribe()
        self.message_user(request, f"Activated {queryset.count()} subscriptions")
    activate_subscriptions.short_description = 'Activate selected subscriptions'

    def deactivate_subscriptions(self, request, queryset):
        for subscription in queryset:
            subscription.unsubscribe()
        self.message_user(request, f"Deactivated {queryset.count()} subscriptions")
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'