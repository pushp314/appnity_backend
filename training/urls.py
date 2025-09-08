from django.urls import path
from . import views

urlpatterns = [
    # Courses
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/featured/', views.featured_courses_view, name='featured-courses'),
    path('courses/stats/', views.course_stats_view, name='course-stats'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    
    # Instructors
    path('instructors/', views.InstructorListView.as_view(), name='instructor-list'),
]