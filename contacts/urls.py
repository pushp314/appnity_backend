from django.urls import path
from . import views

urlpatterns = [
    # Contact form
    path('', views.ContactCreateView.as_view(), name='contact-create'),
    path('list/', views.ContactListView.as_view(), name='contact-list'),
    path('<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('stats/', views.contact_stats_view, name='contact-stats'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe_view, name='newsletter-unsubscribe'),
]