from rest_framework import serializers

from employees.views import get_level
from .models import SalaryRecord, Bonus, YearEndSettlement, Severance, CONFIDENTIAL_LEVEL

MASK = '비공개'


def _is_confidential(employee):
    return get_level(employee) >= CONFIDENTIAL_LEVEL


class SalaryRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.CharField(source='employee.department', read_only=True)
    base_salary = serializers.SerializerMethodField()
    position_allowance = serializers.SerializerMethodField()
    overtime_pay = serializers.SerializerMethodField()
    total_payment = serializers.SerializerMethodField()
    total_deduction = serializers.SerializerMethodField()
    net_pay = serializers.SerializerMethodField()

    class Meta:
        model = SalaryRecord
        fields = [
            'id', 'employee', 'employee_name', 'department', 'period',
            'base_salary', 'position_allowance', 'overtime_pay',
            'total_payment', 'total_deduction', 'net_pay', 'status',
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.lastname}{obj.employee.firstname}"

    def _val(self, obj, value):
        return MASK if _is_confidential(obj.employee) else value

    def get_base_salary(self, obj): return self._val(obj, obj.base_salary)
    def get_position_allowance(self, obj): return self._val(obj, obj.position_allowance)
    def get_overtime_pay(self, obj): return self._val(obj, obj.overtime_pay)
    def get_total_payment(self, obj): return self._val(obj, obj.total_payment)
    def get_total_deduction(self, obj): return self._val(obj, obj.total_deduction)
    def get_net_pay(self, obj): return self._val(obj, obj.net_pay)


class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.CharField(source='employee.department', read_only=True)
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Bonus
        fields = ['id', 'employee', 'employee_name', 'department', 'bonus_type', 'amount', 'pay_date', 'status']

    def get_employee_name(self, obj):
        return f"{obj.employee.lastname}{obj.employee.firstname}"

    def get_amount(self, obj):
        return MASK if _is_confidential(obj.employee) else obj.amount


class YearEndSettlementSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.CharField(source='employee.department', read_only=True)
    total_income = serializers.SerializerMethodField()
    tax_withheld = serializers.SerializerMethodField()
    determined_tax = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()

    class Meta:
        model = YearEndSettlement
        fields = [
            'id', 'employee', 'employee_name', 'department', 'year',
            'total_income', 'tax_withheld', 'determined_tax', 'refund_amount', 'status',
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.lastname}{obj.employee.firstname}"

    def _val(self, obj, value):
        return MASK if _is_confidential(obj.employee) else value

    def get_total_income(self, obj): return self._val(obj, obj.total_income)
    def get_tax_withheld(self, obj): return self._val(obj, obj.tax_withheld)
    def get_determined_tax(self, obj): return self._val(obj, obj.determined_tax)
    def get_refund_amount(self, obj): return self._val(obj, obj.refund_amount)


class SeveranceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    department = serializers.CharField(source='employee.department', read_only=True)
    avg_monthly_wage = serializers.SerializerMethodField()
    calculated_amount = serializers.SerializerMethodField()

    class Meta:
        model = Severance
        fields = [
            'id', 'employee', 'employee_name', 'department',
            'years_of_service', 'avg_monthly_wage', 'calculated_amount', 'status',
        ]

    def get_employee_name(self, obj):
        return f"{obj.employee.lastname}{obj.employee.firstname}"

    def _val(self, obj, value):
        return MASK if _is_confidential(obj.employee) else value

    def get_avg_monthly_wage(self, obj): return self._val(obj, obj.avg_monthly_wage)
    def get_calculated_amount(self, obj): return self._val(obj, obj.calculated_amount)
