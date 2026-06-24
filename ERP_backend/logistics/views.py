from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Vehicle, Dispatch
from .serializers import VehicleSerializer, DispatchSerializer


# =====================================================================
# 1. Vehicle (차량)
# =====================================================================
@api_view(['GET', 'POST'])
def vehicle_list(request):
    if request.method == 'GET':
        vehicles = Vehicle.objects.all()
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'GET':
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = VehicleSerializer(vehicle, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. Dispatch (배차)
# =====================================================================
def _generate_dispatch_code(dispatchdate):
    import datetime
    if isinstance(dispatchdate, str):
        dispatchdate = datetime.date.fromisoformat(dispatchdate)
    # count()+1은 중간 레코드가 삭제되면 기존 코드와 충돌할 수 있어, 실제 존재하는 최대 순번 다음 값을 사용
    existing_codes = Dispatch.objects.filter(dispatchdate=dispatchdate).values_list('code', flat=True)
    max_seq = 0
    for code in existing_codes:
        try:
            max_seq = max(max_seq, int(code.rsplit('-', 1)[-1]))
        except (ValueError, IndexError):
            continue
    return f"DIS-{dispatchdate:%y%m%d}-{max_seq + 1:03d}"


@api_view(['GET', 'POST'])
def dispatch_list(request):
    if request.method == 'GET':
        dispatches = Dispatch.objects.select_related('vehicleid').all()
        serializer = DispatchSerializer(dispatches, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data.copy()
        if not data.get('code'):
            data['code'] = _generate_dispatch_code(data.get('dispatchdate'))
        serializer = DispatchSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def dispatch_detail(request, pk):
    dispatch = get_object_or_404(Dispatch.objects.select_related('vehicleid'), pk=pk)
    if request.method == 'GET':
        serializer = DispatchSerializer(dispatch)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = DispatchSerializer(dispatch, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        dispatch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
