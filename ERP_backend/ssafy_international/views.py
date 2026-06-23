"""
ssafy_international/views.py
- 전부 함수형 뷰(@api_view) + Serializer 사용 (ViewSet 사용 안 함)
- 핵심 영업/재고 도메인: Category, Supplier, Customer, Shipper, Region,
  Territory, Product, Order, OrderDetail
- FK 필드는 픽스처 키 그대로(예: categoryid, supplierid, customerid, shipvia)
  → Product.objects.filter(categoryid=5) 처럼 raw id로 바로 필터 가능
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import (
    Category, Supplier, Customer, Shipper,
    Region, Territory, Product, Order, OrderDetail,
)
from .serializers import (
    CategorySerializer, SupplierSerializer, CustomerSerializer,
    ShipperSerializer, RegionSerializer, TerritorySerializer,
    ProductSerializer, OrderSerializer, OrderdetailSerializer,
)


# =====================================================================
# Category (제품 카테고리) — 전체 CRUD
# =====================================================================
@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        qs = Category.objects.all()
        return Response(CategorySerializer(qs, many=True).data)

    # POST (생성)
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    obj = get_object_or_404(Category, pk=pk)

    if request.method == 'GET':
        return Response(CategorySerializer(obj).data)

    if request.method == 'PUT':
        serializer = CategorySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Supplier (공급사) — 전체 CRUD
# =====================================================================
@api_view(['GET', 'POST'])
def supplier_list(request):
    if request.method == 'GET':
        qs = Supplier.objects.all()
        return Response(SupplierSerializer(qs, many=True).data)

    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def supplier_detail(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)

    if request.method == 'GET':
        return Response(SupplierSerializer(obj).data)

    if request.method == 'PUT':
        serializer = SupplierSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Customer (고객사) — 전체 CRUD (PK = 문자열 customerid)
# =====================================================================
@api_view(['GET', 'POST'])
def customer_list(request):
    if request.method == 'GET':
        qs = Customer.objects.all()
        # 예: ?country=Korea 로 간단 필터 (선택)
        country = request.query_params.get('country')
        if country:
            qs = qs.filter(country=country)
        return Response(CustomerSerializer(qs, many=True).data)

    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def customer_detail(request, pk):
    obj = get_object_or_404(Customer, pk=pk)

    if request.method == 'GET':
        return Response(CustomerSerializer(obj).data)

    if request.method == 'PUT':
        serializer = CustomerSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Product (제품) — 전체 CRUD + categoryid/supplierid 필터
# =====================================================================
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        qs = Product.objects.all()
        # FK 필드명(픽스처 키)으로 바로 필터 가능
        categoryid = request.query_params.get('categoryid')
        supplierid = request.query_params.get('supplierid')
        if categoryid:
            qs = qs.filter(categoryid=categoryid)
        if supplierid:
            qs = qs.filter(supplierid=supplierid)
        return Response(ProductSerializer(qs, many=True).data)

    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    obj = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        return Response(ProductSerializer(obj).data)

    if request.method == 'PUT':
        serializer = ProductSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Order (주문) — 전체 CRUD + customerid/employeeid 필터
# =====================================================================
@api_view(['GET', 'POST'])
def order_list(request):
    if request.method == 'GET':
        qs = Order.objects.all().order_by('-orderdate')
        customerid = request.query_params.get('customerid')
        employeeid = request.query_params.get('employeeid')
        if customerid:
            qs = qs.filter(customerid=customerid)
        if employeeid:
            qs = qs.filter(employeeid=employeeid)
        return Response(OrderSerializer(qs, many=True).data)

    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def order_detail(request, pk):
    obj = get_object_or_404(Order, pk=pk)

    if request.method == 'GET':
        return Response(OrderSerializer(obj).data)

    if request.method == 'PUT':
        serializer = OrderSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# OrderDetail (주문 상세) — 전체 CRUD + orderid 필터
#   ※ Northwind는 (orderid, productid) 복합키지만, Django에서는
#     auto id PK + unique_together(orderid, productid) 가정 → <int:pk>
# =====================================================================
@api_view(['GET', 'POST'])
def orderdetail_list(request):
    if request.method == 'GET':
        qs = OrderDetail.objects.all()
        orderid = request.query_params.get('orderid')
        if orderid:
            qs = qs.filter(orderid=orderid)
        return Response(OrderdetailSerializer(qs, many=True).data)

    serializer = OrderdetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def orderdetail_detail(request, pk):
    obj = get_object_or_404(OrderDetail, pk=pk)

    if request.method == 'GET':
        return Response(OrderdetailSerializer(obj).data)

    if request.method == 'PUT':
        serializer = OrderdetailSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 참조용(거의 안 바뀌는) 테이블 — 조회 전용(list / detail GET)
#   필요해지면 위 패턴대로 POST/PUT/DELETE 추가하면 됨
# =====================================================================
@api_view(['GET'])
def shipper_list(request):
    return Response(ShipperSerializer(Shipper.objects.all(), many=True).data)


@api_view(['GET'])
def shipper_detail(request, pk):
    obj = get_object_or_404(Shipper, pk=pk)
    return Response(ShipperSerializer(obj).data)


@api_view(['GET'])
def region_list(request):
    return Response(RegionSerializer(Region.objects.all(), many=True).data)


@api_view(['GET'])
def region_detail(request, pk):
    obj = get_object_or_404(Region, pk=pk)
    return Response(RegionSerializer(obj).data)


@api_view(['GET'])
def territory_list(request):
    qs = Territory.objects.all()
    regionid = request.query_params.get('regionid')
    if regionid:
        qs = qs.filter(regionid=regionid)
    return Response(TerritorySerializer(qs, many=True).data)


@api_view(['GET'])
def territory_detail(request, pk):
    obj = get_object_or_404(Territory, pk=pk)  # pk = 문자열 territoryid
    return Response(TerritorySerializer(obj).data)