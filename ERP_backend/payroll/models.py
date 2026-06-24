from django.db import models

# 직급(level)별 연 기본급 — 대표이사(레벨5)는 정책상 비공개
ANNUAL_BASE_SALARY = {
    1: 30_000_000,
    2: 35_000_000,
    3: 42_000_000,
    4: 100_000_000,
}
CONFIDENTIAL_LEVEL = 5


class SalaryRecord(models.Model):
    STATUS_CHOICES = [('계산중', '계산중'), ('확정', '확정')]

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, db_column="employeeid", related_name="salary_records",
    )
    period = models.CharField(max_length=7)  # 'YYYY-MM'
    base_salary = models.DecimalField(max_digits=14, decimal_places=0)
    position_allowance = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_deduction = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='확정')

    class Meta:
        db_table = "payroll_salaryrecord"
        unique_together = ("employee", "period")
        ordering = ["-period"]

    @property
    def total_payment(self):
        return self.base_salary + self.position_allowance + self.overtime_pay

    @property
    def net_pay(self):
        return self.total_payment - self.total_deduction


class Bonus(models.Model):
    TYPE_CHOICES = [('설날', '설날'), ('추석', '추석'), ('성과', '성과'), ('특별', '특별')]
    STATUS_CHOICES = [('지급대기', '지급대기'), ('지급완료', '지급완료')]

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, db_column="employeeid", related_name="bonuses",
    )
    bonus_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='성과')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    pay_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='지급완료')

    class Meta:
        db_table = "payroll_bonus"
        ordering = ["-pay_date"]


class YearEndSettlement(models.Model):
    STATUS_CHOICES = [('정산중', '정산중'), ('정산완료', '정산완료')]

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, db_column="employeeid", related_name="year_end_settlements",
    )
    year = models.IntegerField()
    total_income = models.DecimalField(max_digits=14, decimal_places=0)
    tax_withheld = models.DecimalField(max_digits=12, decimal_places=0)
    determined_tax = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='정산완료')

    class Meta:
        db_table = "payroll_yearendsettlement"
        unique_together = ("employee", "year")
        ordering = ["-year"]

    @property
    def refund_amount(self):
        # 양수 = 환급, 음수 = 추가 납부
        return self.tax_withheld - self.determined_tax


class Severance(models.Model):
    STATUS_CHOICES = [('계산됨', '계산됨'), ('지급대기', '지급대기'), ('지급완료', '지급완료')]

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, db_column="employeeid", related_name="severances",
    )
    years_of_service = models.DecimalField(max_digits=5, decimal_places=1)
    avg_monthly_wage = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='계산됨')

    class Meta:
        db_table = "payroll_severance"

    @property
    def calculated_amount(self):
        return self.avg_monthly_wage * self.years_of_service
