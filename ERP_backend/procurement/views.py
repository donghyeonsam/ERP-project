from django.shortcuts import render

from rest_framework import viewsets
from .models import ProductCost, PurchaseOrder, PurchaseOrderDetail, GoodsReceipt, Material, Bom, BomComponent
from .serializers import (
    ProductCostSerializer, 
    PurchaseOrderSerializer, 
    PurchaseOrderDetailSerializer,
    GoodsReceiptSerializer, 
    MaterialSerializer, 
    BomSerializer, 
    BomComponentSerializer
)

# =====================================================================
# 1. ProductCost (제품 원가 / 매입가) ViewSet
# =====================================================================
class ProductCostViewSet(viewsets.ModelViewSet):
    queryset = ProductCost.objects.all()
    serializer_class = ProductCostSerializer


# =====================================================================
# 2. PurchaseOrder & Detail (구매 주문 마스터 및 상세) ViewSet
# =====================================================================
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    # prefetch_related를 써야 하위 details 목록을 긁어올 때 DB 부하(N+1 문제)가 줄어듭니다.
    queryset = PurchaseOrder.objects.all().prefetch_related('details')
    serializer_class = PurchaseOrderSerializer


class PurchaseOrderDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = PurchaseOrderDetailSerializer


# =====================================================================
# 3. GoodsReceipt (상품 입고 / 수령증) ViewSet
# =====================================================================
class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer


# =====================================================================
# 4. Material (원자재 마스터) ViewSet
# =====================================================================
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


# =====================================================================
# 5. Bom & Component (자재 명세서 마스터 및 구성품) ViewSet
# =====================================================================
class BomViewSet(viewsets.ModelViewSet):
    # 마찬가지로 하위 자재 명세(components)를 가져오는 성능 최적화 적용
    queryset = Bom.objects.all().prefetch_related('components')
    serializer_class = BomSerializer


class BomComponentViewSet(viewsets.ModelViewSet):
    queryset = BomComponent.objects.all()
    serializer_class = BomComponentSerializer
