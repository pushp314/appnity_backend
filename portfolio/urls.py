from django.urls import path
from . import views

urlpatterns = [
    # Portfolio projects
    path('', views.PortfolioProjectListView.as_view(), name='portfolio-list'),
    path('featured/', views.featured_projects_view, name='featured-projects'),
    path('category/<str:category>/', views.projects_by_category_view, name='projects-by-category'),
    path('search/', views.search_projects_view, name='search-projects'),
    path('technologies/', views.project_technologies_view, name='project-technologies'),
    path('stats/', views.portfolio_stats_view, name='portfolio-stats'),
    
    # Individual project detail (must be last to avoid conflicts)
    path('<slug:slug>/', views.PortfolioProjectDetailView.as_view(), name='portfolio-detail'),
]