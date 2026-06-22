from rest_framework import serializers
from .models import Employee, EmployeeTerritory


class EmployeeSerializer(serializers.ModelSerializer):

    reports_to_name = serializers.SerializerMethodField()

    role_level = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_reports_to_name(self, obj):
        if obj.reportsto:
            return f"{obj.reportsto.lastname}{obj.reportsto.firstname}"
        return None
    
    def get_role_level(self, obj):
        ROLE_LEVEL = {
            "대표이사": 5,
            "Vice President, Sales": 4,
            "Sales Manager": 3,
            "Inside Sales Coordinator": 2,
            "Sales Representative": 1,
        }
        return ROLE_LEVEL.get(obj.title, 0)


class EmployeeTeritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeTerritory
        fields = '__all__'
