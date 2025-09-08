from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import PortfolioProject, ProjectTechnology, ProjectChallenge, ProjectResult


class ProjectTechnologyInline(admin.TabularInline):
    model = ProjectTechnology
    extra = 1
    fields = ['name', 'category', 'order']


class ProjectChallengeInline(admin.TabularInline):
    model = ProjectChallenge
    extra = 1
    fields = ['title', 'description', 'solution', 'order']


class ProjectResultInline(admin.TabularInline):
    model = ProjectResult
    extra = 1
    fields = ['title', 'description', 'metric', 'order']


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'category', 'status', 'client_name', 'duration', 'is_featured', 'created_at']
    list_filter = ['category', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'subtitle', 'description', 'client_name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectTechnologyInline, ProjectChallengeInline, ProjectResultInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'description', 'category', 'status')
        }),
        ('Media', {
            'fields': ('featured_image', 'gallery_images')
        }),
        ('Links', {
            'fields': ('live_url', 'github_url', 'case_study_url')
        }),
        ('Project Details', {
            'fields': ('client_name', 'duration', 'duration_weeks', 'team_size')
        }),
        ('Metrics', {
            'fields': ('user_count', 'performance_metric', 'business_impact')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'order')
        }),
    )


@admin.register(ProjectTechnology)
class ProjectTechnologyAdmin(admin.ModelAdmin):
    list_display = ['project', 'name', 'category', 'order']
    list_filter = ['project', 'category']
    search_fields = ['name', 'project__title']


@admin.register(ProjectChallenge)
class ProjectChallengeAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'order']
    list_filter = ['project']
    search_fields = ['title', 'description', 'project__title']


@admin.register(ProjectResult)
class ProjectResultAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'metric', 'order']
    list_filter = ['project']
    search_fields = ['title', 'description', 'project__title']