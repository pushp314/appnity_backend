from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductListView(generics.ListAPIView):
    """
    List all products
    """
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_featured']
    ordering = ['order', '-created_at']

    @extend_schema(
        summary="List products",
        description="Get list of all products with filtering options",
        responses={200: ProductListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    """
    Retrieve a product
    """
    queryset = Product.objects.prefetch_related('features', 'technologies', 'metrics')
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

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