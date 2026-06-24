import random
from datetime import date, timedelta

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

    if SalaryRecord.objects.exists():
        return

    today = date.today()
    rng = random.Random(20260624)

    for emp in Employee.objects.exclude(title__isnull=True):
        level = TITLE_LEVEL.get(emp.title, 1)
        annual = ANNUAL_BASE_SALARY[level]
        monthly_base = round(annual / 12)
        allowance = POSITION_ALLOWANCE[level]

        # 급여계산: 최근 3개월
        for i in range(3):
            period_date = add_months(date(today.year, today.month, 1), -i)
            overtime = rng.randint(0, 8) * 50_000
            gross = monthly_base + allowance + overtime
            deduction = round(gross * 0.114)  # 4대보험+소득세 추정 비율
            SalaryRecord.objects.create(
                employee=emp, period=month_str(period_date), base_salary=monthly_base,
                position_allowance=allowance, overtime_pay=overtime, total_deduction=deduction,
                status='확정' if i > 0 else '계산중',
            )

        # 상여관리: 설날 + 추석
        bonus_amount = round(monthly_base * 0.5)
        Bonus.objects.create(employee=emp, bonus_type='설날', amount=bonus_amount, pay_date=date(today.year, 2, 9), status='지급완료')
        Bonus.objects.create(employee=emp, bonus_type='추석', amount=bonus_amount, pay_date=date(today.year, 9, 17), status='지급완료')

        # 연말정산: 전년도
        total_income = annual + allowance * 12
        tax_withheld = round(total_income * 0.04)
        determined_tax = round(tax_withheld * rng.uniform(0.85, 1.15))
        YearEndSettlement.objects.create(
            employee=emp, year=today.year - 1, total_income=total_income,
            tax_withheld=tax_withheld, determined_tax=determined_tax, status='정산완료',
        )

        # 퇴직금: 입사일 기준 근속연수
        if emp.hiredate:
            years = round((today - emp.hiredate).days / 365.25, 1)
        else:
            years = 1.0
        avg_wage = monthly_base + allowance
        Severance.objects.create(employee=emp, years_of_service=years, avg_monthly_wage=avg_wage, status='계산됨')


def unseed(apps, schema_editor):
    for name in ["SalaryRecord", "Bonus", "YearEndSettlement", "Severance"]:
        apps.get_model("payroll", name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("payroll", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
