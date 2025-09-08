from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)


class ProductListView(generics.ListCreateAPIView):
    """
    List all products or create new product (admin only)
    """
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_featured']
    ordering = ['order', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(
        summary="List products",
        description="Get list of all products with filtering options",
        responses={200: ProductListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create product",
        description="Create a new product (admin only)",
        request=ProductCreateUpdateSerializer,
        responses={
            201: ProductDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
        }
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=403
            )
        return super().post(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product
    """
    queryset = Product.objects.prefetch_related('features', 'technologies', 'metrics')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @extend_schema(
        summary="Get product",
        description="Retrieve a single product by slug",
        responses={
            200: ProductDetailSerializer,
            404: OpenApiResponse(description="Product not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update product",
        description="Update a product (admin only)",
        request=ProductCreateUpdateSerializer,
        responses={
            200: ProductDetailSerializer,
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Product not found"),
        }
    )
    def patch(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=403
            )
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete product",
        description="Delete a product (admin only)",
        responses={
            204: OpenApiResponse(description="Product deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin access required"),
            404: OpenApiResponse(description="Product not found"),
        }
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_editor:
            return Response(
                {'error': 'Admin access required'}, 
                status=403
            )
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Get featured products",
    description="Retrieve featured products",
    responses={200: ProductListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products_view(request):
    """
    Get featured products
    """
    featured_products = Product.objects.filter(is_featured=True)
    serializer = ProductListSerializer(featured_products, many=True)
    return Response(serializer.data)