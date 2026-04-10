"""URL configuration for Inventory app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, StockMovementViewSet, products_page

app_name = 'inventory'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = [
    path('', products_page, name='products_page'),
    path('data/', include(router.urls)),
]
