from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF 라우터 초기화
router = DefaultRouter()

# 각각의 ViewSet을 고유한 URL 경로(엔드포인트)에 등록
router.register(r'product-costs', views.ProductCostViewSet, basename='productcost')
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'purchase-order-details', views.PurchaseOrderDetailViewSet, basename='purchaseorderdetail')
router.register(r'goods-receipts', views.GoodsReceiptViewSet, basename='goodsreceipt')
router.register(r'materials', views.MaterialViewSet, basename='material')
router.register(r'boms', views.BomViewSet, basename='bom')
router.register(r'bom-components', views.BomComponentViewSet, basename='bomcomponent')

# 메인 프로젝트 urls.py가 "api/v1/procurement/"로 이 파일을 인클루드하고 있으므로,
# 최종 주소는 아래와 같이 자동으로 매핑됩니다.
urlpatterns = [
    path('', include(router.urls)),
]