"""
ssafy_international/urls.py
- config 에서 path('api/v1/ssafy/', include('ssafy_international.urls')) 형태로 포함
- Customer / Territory 는 문자열 PK 이므로 <str:pk> 사용
"""
from django.urls import path
from . import views

app_name = 'ssafy_international'

urlpatterns = [
    # Category
    path('categories/', views.category_list),
    path('categories/<int:pk>/', views.category_detail),

    # Supplier
    path('suppliers/', views.supplier_list),
    path('suppliers/<int:pk>/', views.supplier_detail),

    # Customer (문자열 PK)
    path('customers/', views.customer_list),
    path('customers/<str:pk>/', views.customer_detail),

    # Product
    path('products/', views.product_list),
    path('products/<int:pk>/', views.product_detail),

    # Order
    path('orders/', views.order_list),
    path('orders/<int:pk>/', views.order_detail),

    # OrderDetail
    path('order-details/', views.orderdetail_list),
    path('order-details/<int:pk>/', views.orderdetail_detail),

    # 참조 테이블 (조회 전용)
    path('shippers/', views.shipper_list),
    path('shippers/<int:pk>/', views.shipper_detail),
    path('regions/', views.region_list),
    path('regions/<int:pk>/', views.region_detail),
    path('territories/', views.territory_list),
    path('territories/<str:pk>/', views.territory_detail),  # 문자열 PK
]