import random
from datetime import date, timedelta

from django.db import migrations


def seed(apps, schema_editor):
    Product = apps.get_model("ssafy_international", "Product")
    Employee = apps.get_model("employees", "Employee")
    InventoryCountPlan = apps.get_model("inventory", "InventoryCountPlan")
    InventoryCountItem = apps.get_model("inventory", "InventoryCountItem")

    if InventoryCountPlan.objects.exists():
        return

    today = date.today()
    rng = random.Random(20260624)

    plans_spec = [
        {
            "count_type": "정기", "scope": "완제품창고 전체", "warehouse": "경기물류센터",
            "scheduled_date": today - timedelta(days=10), "manager_id": 5, "status": "완료",
            "product_ids": [1, 2, 3, 4, 5], "fully_counted": True,
        },
        {
            "count_type": "특별", "scope": "유제품 전체", "warehouse": "중앙물류센터",
            "scheduled_date": today - timedelta(days=3), "manager_id": 2, "status": "진행중",
            "product_ids": [11, 12, 31, 32], "fully_counted": False,
        },
        {
            "count_type": "수시", "scope": "수산물 전체", "warehouse": "부산물류센터",
            "scheduled_date": today + timedelta(days=4), "manager_id": 3, "status": "대기",
            "product_ids": [59, 60, 69], "fully_counted": None,
        },
    ]

    for idx, spec in enumerate(plans_spec, start=1):
        manager = Employee.objects.filter(pk=spec["manager_id"]).first()
        plan = InventoryCountPlan.objects.create(
            code=f"CNT-{spec['scheduled_date']:%y%m%d}-{idx:03d}",
            count_type=spec["count_type"],
            scope=spec["scope"],
            warehouse=spec["warehouse"],
            scheduled_date=spec["scheduled_date"],
            manager=manager,
            status=spec["status"],
        )
        for pos, pid in enumerate(spec["product_ids"]):
            product = Product.objects.filter(pk=pid).first()
            if not product:
                continue
            system_qty = product.unitsinstock or rng.randint(10, 100)
            if spec["fully_counted"] is True:
                # 완료 plan: 한두 건만 약간의 차이를 두어 "일치율" 지표가 의미 있게 나오도록
                diff = -2 if pos == 1 else 0
                counted_qty = max(system_qty + diff, 0)
            elif spec["fully_counted"] is False:
                # 진행중 plan: 절반만 입력 완료
                counted_qty = system_qty if pos % 2 == 0 else None
            else:
                counted_qty = None
            InventoryCountItem.objects.create(
                plan=plan, product=product, system_qty=system_qty, counted_qty=counted_qty,
            )


def unseed(apps, schema_editor):
    InventoryCountPlan = apps.get_model("inventory", "InventoryCountPlan")
    InventoryCountPlan.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
