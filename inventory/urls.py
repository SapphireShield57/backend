from django.urls import path
from . import views

urlpatterns = [
    path('product/id/<int:pk>/', views.product_detail, name='product-detail'),
    path('product/qr/<str:qr_code>/', views.get_product_by_qr, name='get_product_by_qr'),
    path('product/', views.list_products, name='product-list'),
    path('product/stock-update/<int:pk>/', views.stock_update, name='stock-update'),
    path('product/total-stock/', views.total_stock, name='total-stock'),
    path('product/<int:pk>/history/', views.product_history, name='product-history'),
]


