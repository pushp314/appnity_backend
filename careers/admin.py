from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import JobPosition, JobSkill, JobApplication


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 1
    fields = ['name', 'skill_type', 'experience_years', 'order']


@admin.register(JobPosition)
class JobPositionAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'department', 'job_type', 'level', 'location', 'status', 'is_featured', 'created_at']
    list_filter = ['department', 'job_type', 'level', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'department', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [JobSkillInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'department', 'job_type', 'level', 'location')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'equity_offered')
        }),
        ('Application', {
            'fields': ('application_deadline', 'application_email', 'application_url')
        }),
        ('Status & Display', {
            'fields': ('status', 'is_featured', 'order')
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'email', 'years_of_experience', 'status', 'created_at']
    list_filter = ['status', 'position', 'years_of_experience', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'position__title']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_reviewing', 'mark_as_interview', 'mark_as_rejected']

    fieldsets = (
        ('Applicant Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'location')
        }),
        ('Application Details', {
            'fields': ('position', 'cover_letter', 'resume', 'portfolio_url', 'github_url', 'linkedin_url')
        }),
        ('Experience & Salary', {
            'fields': ('years_of_experience', 'current_salary', 'expected_salary')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_reviewing(self, request, queryset):
        queryset.update(status='reviewing')
    mark_as_reviewing.short_description = 'Mark as under review'

    def mark_as_interview(self, request, queryset):
        queryset.update(status='interview')
    mark_as_interview.short_description = 'Mark as interview scheduled'

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = 'Mark as rejected'


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ['position', 'name', 'skill_type', 'experience_years', 'order']
    list_filter = ['skill_type', 'position']
    search_fields = ['name', 'position__title']