from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404

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
# 1. ProductCost (제품 원가)
# =====================================================================
@api_view(['GET', 'POST'])
def product_cost_list(request):
    if request.method == 'GET':
        costs = ProductCost.objects.all()
        serializer = ProductCostSerializer(costs, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductCostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def product_cost_detail(request, pk):
    cost = get_object_or_404(ProductCost, pk=pk)
    if request.method == 'GET':
        serializer = ProductCostSerializer(cost)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductCostSerializer(cost, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        cost.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. PurchaseOrder (구매 주문 마스터)
# =====================================================================
@api_view(['GET', 'POST'])
def purchase_order_list(request):
    if request.method == 'GET':
        orders = PurchaseOrder.objects.all().prefetch_related('details')
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder.objects.prefetch_related('details'), pk=pk)
    if request.method == 'GET':
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PurchaseOrderSerializer(order, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 3. PurchaseOrderDetail (구매 주문 상세)
# =====================================================================
@api_view(['GET', 'POST'])
def purchase_order_detail_list(request):
    if request.method == 'GET':
        details = PurchaseOrderDetail.objects.all()
        serializer = PurchaseOrderDetailSerializer(details, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = PurchaseOrderDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def purchase_order_detail_item(request, pk):
    detail = get_object_or_404(PurchaseOrderDetail, pk=pk)
    if request.method == 'GET':
        serializer = PurchaseOrderDetailSerializer(detail)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PurchaseOrderDetailSerializer(detail, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 4. GoodsReceipt (상품 입고)
# =====================================================================
@api_view(['GET', 'POST'])
def goods_receipt_list(request):
    if request.method == 'GET':
        receipts = GoodsReceipt.objects.all()
        serializer = GoodsReceiptSerializer(receipts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = GoodsReceiptSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def goods_receipt_detail(request, pk):
    receipt = get_object_or_404(GoodsReceipt, pk=pk)
    if request.method == 'GET':
        serializer = GoodsReceiptSerializer(receipt)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = GoodsReceiptSerializer(receipt, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        receipt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 5. Material (원자재 마스터)
# =====================================================================
@api_view(['GET', 'POST'])
def material_list(request):
    if request.method == 'GET':
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'GET':
        serializer = MaterialSerializer(material)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = MaterialSerializer(material, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        material.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 6. Bom (자재 명세서 마스터)
# =====================================================================
@api_view(['GET', 'POST'])
def bom_list(request):
    if request.method == 'GET':
        boms = Bom.objects.all().prefetch_related('components')
        serializer = BomSerializer(boms, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def bom_detail(request, pk):
    bom = get_object_or_404(Bom.objects.prefetch_related('components'), pk=pk)
    if request.method == 'GET':
        serializer = BomSerializer(bom)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BomSerializer(bom, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        bom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 7. BomComponent (자재 명세서 구성품)
# =====================================================================
@api_view(['GET', 'POST'])
def bom_component_list(request):
    if request.method == 'GET':
        components = BomComponent.objects.all()
        serializer = BomComponentSerializer(components, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BomComponentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def bom_component_detail(request, pk):
    component = get_object_or_404(BomComponent, pk=pk)
    if request.method == 'GET':
        serializer = BomComponentSerializer(component)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BomComponentSerializer(component, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        component.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)