from django.urls import path
from . import views

urlpatterns = [
    # Testimonials
    path('', views.TestimonialListView.as_view(), name='testimonial-list'),
    path('<int:pk>/', views.TestimonialDetailView.as_view(), name='testimonial-detail'),
    path('featured/', views.featured_testimonials_view, name='featured-testimonials'),
    path('type/<str:testimonial_type>/', views.testimonials_by_type_view, name='testimonials-by-type'),
    
    # Testimonial submissions
    path('submit/', views.TestimonialSubmissionCreateView.as_view(), name='testimonial-submit'),
    
    # Statistics
    path('stats/', views.testimonial_stats_view, name='testimonial-stats'),
]