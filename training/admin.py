from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Course, CourseModule, CourseTechnology, CourseProject, Instructor, CourseInstructor


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ['title', 'description', 'duration', 'order']


class CourseTechnologyInline(admin.TabularInline):
    model = CourseTechnology
    extra = 1
    fields = ['name', 'category', 'order']


class CourseProjectInline(admin.TabularInline):
    model = CourseProject
    extra = 1
    fields = ['title', 'description', 'difficulty', 'order']


class CourseInstructorInline(admin.TabularInline):
    model = CourseInstructor
    extra = 1
    fields = ['instructor', 'role', 'order']


@admin.register(Course)
class CourseAdmin(MarkdownxModelAdmin):
    list_display = ['title', 'level', 'status', 'price', 'student_count', 'rating', 'is_featured', 'created_at']
    list_filter = ['level', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseModuleInline, CourseTechnologyInline, CourseProjectInline, CourseInstructorInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'description', 'level', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Course Details', {
            'fields': ('duration', 'featured_image', 'preview_video_url')
        }),
        ('Metrics', {
            'fields': ('student_count', 'rating', 'completion_rate')
        }),
        ('SEO & Display', {
            'fields': ('meta_description', 'is_featured', 'order')
        }),
    )


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'experience_years', 'created_at']
    search_fields = ['name', 'title', 'bio']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'bio', 'avatar', 'experience_years')
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'twitter_url', 'website_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'duration', 'order']
    list_filter = ['course']
    search_fields = ['title', 'description']


@admin.register(CourseTechnology)
class CourseTechnologyAdmin(admin.ModelAdmin):
    list_display = ['course', 'name', 'category', 'order']
    list_filter = ['course', 'category']
    search_fields = ['name']


@admin.register(CourseProject)
class CourseProjectAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'difficulty', 'order']
    list_filter = ['course', 'difficulty']
    search_fields = ['title', 'description']