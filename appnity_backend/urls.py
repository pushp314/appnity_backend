"""
URL configuration for appnity_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/blogs/', include('blogs.urls')),
    path('api/v1/contacts/', include('contacts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/portfolio/', include('portfolio.urls')),
    path('api/v1/training/', include('training.urls')),
    path('api/v1/careers/', include('careers.urls')),
    path('api/v1/testimonials/', include('testimonials.urls')),
    path('api/v1/newsletter/', include('newsletter.urls')),
    
    # Markdown editor
    path('markdownx/', include('markdownx.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom admin configuration
admin.site.site_header = "Appnity Admin"
admin.site.site_title = "Appnity Admin Portal"
admin.site.index_title = "Welcome to Appnity Administration"