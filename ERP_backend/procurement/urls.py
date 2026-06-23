from django.urls import path
from . import views

urlpatterns = [
    # 1. ProductCost
    path('product-costs/', views.product_cost_list, name='product_cost_list'),
    path('product-costs/<int:pk>/', views.product_cost_detail, name='product_cost_detail'),

    # 2. PurchaseOrder
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),

    # 3. PurchaseOrderDetail
    path('purchase-order-details/', views.purchase_order_detail_list, name='purchase_order_detail_list'),
    path('purchase-order-details/<int:pk>/', views.purchase_order_detail_item, name='purchase_order_detail_item'),

    # 4. GoodsReceipt
    path('goods-receipts/', views.goods_receipt_list, name='goods_receipt_list'),
    path('goods-receipts/<int:pk>/', views.goods_receipt_detail, name='goods_receipt_detail'),

    # 5. Material
    path('materials/', views.material_list, name='material_list'),
    path('materials/<str:pk>/', views.material_detail, name='material_detail'), # Material ID는 CharField이므로 <str:pk>

    # 6. Bom
    path('boms/', views.bom_list, name='bom_list'),
    path('boms/<int:pk>/', views.bom_detail, name='bom_detail'),

    # 7. BomComponent
    path('bom-components/', views.bom_component_list, name='bom_component_list'),
    path('bom-components/<int:pk>/', views.bom_component_detail, name='bom_component_detail'),
]