from django.db import models


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    platenumber = models.CharField(max_length=20)               # 예: "34가 5678"
    capacitylabel = models.CharField(max_length=20)             # 예: "5톤", "1톤"
    capacitykg = models.IntegerField(default=0)                 # 최대 적재량(kg), 적재율 계산용

    class Meta:
        db_table = "vehicle"

    def __str__(self):
        return f"{self.platenumber} ({self.capacitylabel})"


class Dispatch(models.Model):
    STATUS_CHOICES = [
        ("waiting", "대기"),
        ("in_transit", "배송중"),
        ("completed", "완료"),
    ]

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)         # 예: "DIS-260323-001"
    dispatchdate = models.DateField()
    vehicleid = models.ForeignKey(Vehicle, on_delete=models.PROTECT, db_column="vehicleid", related_name="dispatches")
    drivername = models.CharField(max_length=40)
    region = models.CharField(max_length=100)
    shipmentcount = models.IntegerField(default=0)
    totalweightkg = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    departuretime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")

    class Meta:
        db_table = "dispatch"
        ordering = ["departuretime"]

    def __str__(self):
        return f"{self.code} ({self.get_status_display()})"
