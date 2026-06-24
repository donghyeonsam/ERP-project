from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import InventoryCountPlan, InventoryCountItem
from .serializers import InventoryCountPlanSerializer, InventoryCountItemSerializer


def _generate_plan_code(scheduled_date):
    import datetime
    if isinstance(scheduled_date, str):
        scheduled_date = datetime.date.fromisoformat(scheduled_date)
    existing_codes = InventoryCountPlan.objects.filter(scheduled_date=scheduled_date).values_list('code', flat=True)
    max_seq = 0
    for code in existing_codes:
        try:
            max_seq = max(max_seq, int(code.rsplit('-', 1)[-1]))
        except (ValueError, IndexError):
            continue
    return f"CNT-{scheduled_date:%y%m%d}-{max_seq + 1:03d}"


# =====================================================================
# 1. InventoryCountPlan (실사계획)
# =====================================================================
@api_view(['GET', 'POST'])
def count_plan_list(request):
    if request.method == 'GET':
        plans = InventoryCountPlan.objects.select_related('manager').prefetch_related('items__product')
        return Response(InventoryCountPlanSerializer(plans, many=True).data)

    data = request.data.copy()
    if not data.get('code'):
        data['code'] = _generate_plan_code(data.get('scheduled_date'))
    serializer = InventoryCountPlanSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        plan = InventoryCountPlan.objects.create(
            code=data['code'],
            count_type=data.get('count_type', '정기'),
            scope=data.get('scope'),
            warehouse=data.get('warehouse'),
            scheduled_date=data.get('scheduled_date'),
            manager_id=data.get('manager') or None,
            status=data.get('status', '대기'),
        )
        return Response(InventoryCountPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def count_plan_detail(request, pk):
    plan = get_object_or_404(InventoryCountPlan, pk=pk)

    if request.method == 'GET':
        return Response(InventoryCountPlanSerializer(plan).data)

    if request.method == 'PUT':
        for field in ['count_type', 'scope', 'warehouse', 'scheduled_date', 'status']:
            if field in request.data:
                setattr(plan, field, request.data[field])
        if 'manager' in request.data:
            plan.manager_id = request.data['manager']
        plan.save()
        return Response(InventoryCountPlanSerializer(plan).data)

    plan.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. InventoryCountItem (실사등록 / 차이조정)
# =====================================================================
@api_view(['GET', 'POST'])
def count_item_list(request):
    if request.method == 'GET':
        items = InventoryCountItem.objects.select_related('product', 'plan')
        plan_id = request.query_params.get('plan')
        if plan_id:
            items = items.filter(plan_id=plan_id)
        return Response(InventoryCountItemSerializer(items, many=True).data)

    serializer = InventoryCountItemSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def count_item_detail(request, pk):
    item = get_object_or_404(InventoryCountItem, pk=pk)

    if request.method == 'GET':
        return Response(InventoryCountItemSerializer(item).data)

    if request.method == 'PUT':
        serializer = InventoryCountItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
