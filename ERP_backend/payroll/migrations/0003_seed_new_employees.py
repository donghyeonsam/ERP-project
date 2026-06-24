import random
from datetime import date

from django.db import migrations

ANNUAL_BASE_SALARY = {1: 30_000_000, 2: 35_000_000, 3: 42_000_000, 4: 100_000_000, 5: 220_000_000}
TITLE_LEVEL = {
    '대표이사': 5,
    'Vice President, Sales': 4,
    'Sales Manager': 3,
    'Inside Sales Coordinator': 2,
    'Sales Representative': 1,
}
POSITION_ALLOWANCE = {5: 2_000_000, 4: 1_500_000, 3: 800_000, 2: 300_000, 1: 0}


def month_str(d):
    return f"{d.year:04d}-{d.month:02d}"


def add_months(d, months):
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)


def seed(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    SalaryRecord = apps.get_model("payroll", "SalaryRecord")
    Bonus = apps.get_model("payroll", "Bonus")
    YearEndSettlement = apps.get_model("payroll", "YearEndSettlement")
    Severance = apps.get_model("payroll", "Severance")

    today = date.today()
    rng = random.Random(20260625)

    # 0002에서 이미 시드된 직원은 건드리지 않고, 아직 급여 기록이 없는 직원(신규 입사자)만 채운다
    for emp in Employee.objects.exclude(title__isnull=True):
        if SalaryRecord.objects.filter(employee=emp).exists():
            continue

        level = TITLE_LEVEL.get(emp.title, 1)
        annual = ANNUAL_BASE_SALARY[level]
        monthly_base = round(annual / 12)
        allowance = POSITION_ALLOWANCE[level]

        for i in range(3):
            period_date = add_months(date(today.year, today.month, 1), -i)
            overtime = rng.randint(0, 8) * 50_000
            gross = monthly_base + allowance + overtime
            deduction = round(gross * 0.114)
            SalaryRecord.objects.create(
                employee=emp, period=month_str(period_date), base_salary=monthly_base,
                position_allowance=allowance, overtime_pay=overtime, total_deduction=deduction,
                status='확정' if i > 0 else '계산중',
            )

        bonus_amount = round(monthly_base * 0.5)
        Bonus.objects.create(employee=emp, bonus_type='설날', amount=bonus_amount, pay_date=date(today.year, 2, 9), status='지급완료')
        Bonus.objects.create(employee=emp, bonus_type='추석', amount=bonus_amount, pay_date=date(today.year, 9, 17), status='지급완료')

        total_income = annual + allowance * 12
        tax_withheld = round(total_income * 0.04)
        determined_tax = round(tax_withheld * rng.uniform(0.85, 1.15))
        YearEndSettlement.objects.create(
            employee=emp, year=today.year - 1, total_income=total_income,
            tax_withheld=tax_withheld, determined_tax=determined_tax, status='정산완료',
        )

        if emp.hiredate:
            years = round((today - emp.hiredate).days / 365.25, 1)
        else:
            years = 1.0
        avg_wage = monthly_base + allowance
        Severance.objects.create(employee=emp, years_of_service=years, avg_monthly_wage=avg_wage, status='계산됨')


def unseed(apps, schema_editor):
    # 0002가 이미 만든 기존 10명 데이터는 그대로 두고, 이 마이그레이션이 만든 것만 되돌리기는
    # 식별이 어려우므로 역방향은 단순 no-op으로 둔다 (필요 시 전체 재시드로 처리).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0002_seed_payroll"),
        ("employees", "0005_rename_and_expand_roster"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
