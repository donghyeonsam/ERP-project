from django.db import models


class InventoryCountPlan(models.Model):
    TYPE_CHOICES = [
        ('정기', '정기'),
        ('특별', '특별'),
        ('수시', '수시'),
    ]
    STATUS_CHOICES = [
        ('대기', '대기'),
        ('진행중', '진행중'),
        ('완료', '완료'),
    ]

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)             # 예: "CNT-260624-001"
    count_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='정기', db_column="count_type")
    scope = models.CharField(max_length=100, blank=True, null=True)  # 예: "전체 품목", "유제품 전체"
    warehouse = models.CharField(max_length=40)
    scheduled_date = models.DateField(db_column="scheduled_date")
    manager = models.ForeignKey(
        "employees.Employee", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="manager_id", related_name="inventory_count_plans",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='대기')

    class Meta:
        db_table = "inventorycountplan"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.code} ({self.status})"

    @property
    def progress_rate(self):
        total = self.items.count()
        if not total:
            return 0
        counted = self.items.exclude(counted_qty__isnull=True).count()
        return round(counted / total * 100)


class InventoryCountItem(models.Model):
    id = models.AutoField(primary_key=True)
    plan = models.ForeignKey(InventoryCountPlan, on_delete=models.CASCADE, db_column="plan_id", related_name="items")
    product = models.ForeignKey("ssafy_international.Product", on_delete=models.PROTECT, db_column="productid", related_name="count_items")
    system_qty = models.IntegerField(default=0)                      # 실사 시점 전산 재고
    counted_qty = models.IntegerField(null=True, blank=True)         # 실사 입력 전까지는 null
    note = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "inventorycountitem"

    @property
    def diff(self):
        if self.counted_qty is None:
            return None
        return self.counted_qty - self.system_qty
