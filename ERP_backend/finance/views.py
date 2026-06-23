from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404

from .models import Expense, AccountsReceivable, AccountsPayable
from .serializers import ExpenseSerializer, AccountsReceivableSerializer, AccountsPayableSerializer

# =====================================================================
# 1. Expense (일반 경비 / 지출)
# =====================================================================
@api_view(['GET', 'POST'])
def expense_list(request):
    if request.method == 'GET':
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. AccountsReceivable (매출채권 / 받을 돈)
# =====================================================================
@api_view(['GET', 'POST'])
def accounts_receivable_list(request):
    if request.method == 'GET':
        # select_related를 통해 외래키 데이터를 단일 Query(JOIN)로 최적화 조회
        receivables = AccountsReceivable.objects.all().select_related('orderid', 'customerid')
        serializer = AccountsReceivableSerializer(receivables, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = AccountsReceivableSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def accounts_receivable_detail(request, pk):
    receivable = get_object_or_404(
        AccountsReceivable.objects.select_related('orderid', 'customerid'), 
        pk=pk
    )
    
    if request.method == 'GET':
        serializer = AccountsReceivableSerializer(receivable)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = AccountsReceivableSerializer(receivable, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        receivable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 3. AccountsPayable (매입채무 / 줄 돈)
# =====================================================================
@api_view(['GET', 'POST'])
def accounts_payable_list(request):
    if request.method == 'GET':
        # select_related를 통해 외래키 데이터를 단일 Query(JOIN)로 최적화 조회
        payables = AccountsPayable.objects.all().select_related('purchaseorderid', 'supplierid')
        serializer = AccountsPayableSerializer(payables, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = AccountsPayableSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def accounts_payable_detail(request, pk):
    payable = get_object_or_404(
        AccountsPayable.objects.select_related('purchaseorderid', 'supplierid'), 
        pk=pk
    )
    
    if request.method == 'GET':
        serializer = AccountsPayableSerializer(payable)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = AccountsPayableSerializer(payable, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        payable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)