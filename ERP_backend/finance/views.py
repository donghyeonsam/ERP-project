from django.shortcuts import render

from rest_framework import viewsets
from .models import Expense, AccountsReceivable, AccountsPayable
from .serializers import ExpenseSerializer, AccountsReceivableSerializer, AccountsPayableSerializer

# =====================================================================
# 1. Expense (일반 경비 / 지출) ViewSet
# =====================================================================
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


# =====================================================================
# 2. AccountsReceivable (매출채권 / 받을 돈) ViewSet
# =====================================================================
class AccountsReceivableViewSet(viewsets.ModelViewSet):
    # select_related를 통해 연결된 외래키 마스터 데이터를 단일 Query(JOIN)로 최적화 조회합니다.
    queryset = AccountsReceivable.objects.all().select_related('orderid', 'customerid')
    serializer_class = AccountsReceivableSerializer


# =====================================================================
# 3. AccountsPayable (매입채무 / 줄 돈) ViewSet
# =====================================================================
class AccountsPayableViewSet(viewsets.ModelViewSet):
    # select_related를 통해 연결된 외래키 마스터 데이터를 단일 Query(JOIN)로 최적화 조회합니다.
    queryset = AccountsPayable.objects.all().select_related('purchaseorderid', 'supplierid')
    serializer_class = AccountsPayableSerializer