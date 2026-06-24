from rest_framework import serializers
from .models import Budget, Expense, AccountsReceivable, AccountsPayable

# =====================================================================
# 0. Budget (부서별 예산 편성) Serializer
# =====================================================================
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'


# =====================================================================
# 1. Expense (일반 경비 / 지출) Serializer
# =====================================================================
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'


# =====================================================================
# 2. AccountsReceivable (매출채권 / 받을 돈) Serializer
# =====================================================================
class AccountsReceivableSerializer(serializers.ModelSerializer):
    # Vue 3 SPA 화면에서 직관적으로 보여주기 위한 가독성용 읽기 전용 필드들
    customer_name = serializers.CharField(source='customerid.companyname', read_only=True)
    # 원본 주문의 일자나 담당자 정보를 프론트엔드에서 바로 보여주고 싶을 때 유용합니다.
    order_date = serializers.DateTimeField(source='orderid.orderdate', read_only=True)

    class Meta:
        model = AccountsReceivable
        fields = [
            'id', 'orderid', 'order_date', 'customerid', 'customer_name',
            'invoicedate', 'duedate', 'amount', 'currency', 'paymentterms', 'status'
        ]


# =====================================================================
# 3. AccountsPayable (매입채무 / 줄 돈) Serializer
# =====================================================================
class AccountsPayableSerializer(serializers.ModelSerializer):
    # Vue 3 SPA 화면에서 직관적으로 보여주기 위한 가독성용 읽기 전용 필드들
    supplier_name = serializers.CharField(source='supplierid.companyname', read_only=True)
    # 원본 구매 주문의 발주일자를 프론트엔드에서 연동하여 보여주기 위함입니다.
    purchase_order_date = serializers.DateField(source='purchaseorderid.orderdate', read_only=True)

    class Meta:
        model = AccountsPayable
        fields = [
            'id', 'purchaseorderid', 'purchase_order_date', 'supplierid', 'supplier_name',
            'invoicedate', 'duedate', 'amount', 'currency', 'paymentterms', 'status'
        ]