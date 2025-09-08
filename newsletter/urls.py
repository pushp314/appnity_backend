from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('unsubscribe/', views.newsletter_unsubscribe_view, name='newsletter-unsubscribe'),
    path('list/', views.NewsletterListView.as_view(), name='newsletter-list'),
    path('stats/', views.newsletter_stats_view, name='newsletter-stats'),
]