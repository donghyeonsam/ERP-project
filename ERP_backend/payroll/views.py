from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import SalaryRecord, Bonus, YearEndSettlement, Severance
from .serializers import (
    SalaryRecordSerializer, BonusSerializer, YearEndSettlementSerializer, SeveranceSerializer,
)


# =====================================================================
# 1. SalaryRecord (급여계산)
# =====================================================================
@api_view(['GET', 'POST'])
def salary_list(request):
    if request.method == 'GET':
        qs = SalaryRecord.objects.select_related('employee').all()
        return Response(SalaryRecordSerializer(qs, many=True).data)

    serializer = SalaryRecordSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def salary_detail(request, pk):
    obj = get_object_or_404(SalaryRecord, pk=pk)
    if request.method == 'GET':
        return Response(SalaryRecordSerializer(obj).data)
    if request.method == 'PUT':
        serializer = SalaryRecordSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. Bonus (상여관리)
# =====================================================================
@api_view(['GET', 'POST'])
def bonus_list(request):
    if request.method == 'GET':
        qs = Bonus.objects.select_related('employee').all()
        return Response(BonusSerializer(qs, many=True).data)

    serializer = BonusSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def bonus_detail(request, pk):
    obj = get_object_or_404(Bonus, pk=pk)
    if request.method == 'GET':
        return Response(BonusSerializer(obj).data)
    if request.method == 'PUT':
        serializer = BonusSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 3. YearEndSettlement (연말정산)
# =====================================================================
@api_view(['GET', 'POST'])
def yearend_list(request):
    if request.method == 'GET':
        qs = YearEndSettlement.objects.select_related('employee').all()
        return Response(YearEndSettlementSerializer(qs, many=True).data)

    serializer = YearEndSettlementSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def yearend_detail(request, pk):
    obj = get_object_or_404(YearEndSettlement, pk=pk)
    if request.method == 'GET':
        return Response(YearEndSettlementSerializer(obj).data)
    if request.method == 'PUT':
        serializer = YearEndSettlementSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 4. Severance (퇴직금관리)
# =====================================================================
@api_view(['GET', 'POST'])
def severance_list(request):
    if request.method == 'GET':
        qs = Severance.objects.select_related('employee').all()
        return Response(SeveranceSerializer(qs, many=True).data)

    serializer = SeveranceSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def severance_detail(request, pk):
    obj = get_object_or_404(Severance, pk=pk)
    if request.method == 'GET':
        return Response(SeveranceSerializer(obj).data)
    if request.method == 'PUT':
        serializer = SeveranceSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
