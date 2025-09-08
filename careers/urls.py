from django.urls import path
from . import views

urlpatterns = [
    # Job positions
    path('positions/', views.JobPositionListView.as_view(), name='job-position-list'),
    path('positions/open/', views.open_positions_view, name='open-positions'),
    path('positions/<slug:slug>/', views.JobPositionDetailView.as_view(), name='job-position-detail'),
    
    # Job applications
    path('positions/<slug:position_slug>/apply/', views.JobApplicationCreateView.as_view(), name='job-application-create'),
    path('applications/', views.JobApplicationListView.as_view(), name='job-application-list'),
    path('applications/<int:pk>/', views.JobApplicationDetailView.as_view(), name='job-application-detail'),
    
    # Statistics
    path('stats/', views.career_stats_view, name='career-stats'),
]