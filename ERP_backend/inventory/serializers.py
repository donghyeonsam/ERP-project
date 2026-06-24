from rest_framework import serializers
from .models import InventoryCountPlan, InventoryCountItem


class InventoryCountItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.productname', read_only=True)
    diff = serializers.SerializerMethodField()

    class Meta:
        model = InventoryCountItem
        fields = ['id', 'plan', 'product', 'product_name', 'system_qty', 'counted_qty', 'diff', 'note']

    def get_diff(self, obj):
        return obj.diff


class InventoryCountPlanSerializer(serializers.ModelSerializer):
    items = InventoryCountItemSerializer(many=True, read_only=True)
    manager_name = serializers.SerializerMethodField()
    progress_rate = serializers.ReadOnlyField()

    class Meta:
        model = InventoryCountPlan
        fields = [
            'id', 'code', 'count_type', 'scope', 'warehouse', 'scheduled_date',
            'manager', 'manager_name', 'status', 'progress_rate', 'items',
        ]

    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.lastname}{obj.manager.firstname}"
        return None
