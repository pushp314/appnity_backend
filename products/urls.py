from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('featured/', views.featured_products_view, name='featured-products'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]