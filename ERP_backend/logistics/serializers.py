from rest_framework import serializers
from .models import Vehicle, Dispatch


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class DispatchSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source="vehicleid.platenumber", read_only=True)
    vehicle_capacity_label = serializers.CharField(source="vehicleid.capacitylabel", read_only=True)
    vehicle_capacity_kg = serializers.IntegerField(source="vehicleid.capacitykg", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    load_rate = serializers.SerializerMethodField()

    class Meta:
        model = Dispatch
        fields = [
            "id", "code", "dispatchdate", "vehicleid",
            "vehicle_plate", "vehicle_capacity_label", "vehicle_capacity_kg",
            "drivername", "region", "shipmentcount", "totalweightkg",
            "departuretime", "status", "status_label", "load_rate",
        ]

    def get_load_rate(self, obj):
        capacity = obj.vehicleid.capacitykg
        if not capacity:
            return 0
        return round(float(obj.totalweightkg) / capacity * 100)
