import random

from django.db import migrations


def reseed_budget(apps, schema_editor):
    Expense = apps.get_model("finance", "Expense")
    Budget = apps.get_model("finance", "Budget")

    # 데이터 증강으로 Expense(실적)가 교체되어 기존 Budget(예산) 시드와 기간이 어긋났으므로 재시드
    Budget.objects.all().delete()

    budgets = []
    for expense in Expense.objects.all():
        target_achievement = random.Random(expense.id).uniform(0.83, 1.22)
        budget_amount = round(float(expense.amount) / target_achievement, 2)
        budgets.append(
            Budget(
                period=expense.period,
                costcenter=expense.costcenter,
                category=expense.category,
                amount=budget_amount,
                currency=expense.currency,
            )
        )
    Budget.objects.bulk_create(budgets)


def unreseed_budget(apps, schema_editor):
    # 역방향 마이그레이션 시에는 이전 상태로 정확히 복원할 수 없으므로 비워둔다
    Budget = apps.get_model("finance", "Budget")
    Budget.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(reseed_budget, unreseed_budget),
    ]
