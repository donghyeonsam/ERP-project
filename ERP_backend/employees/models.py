# employees/models.py
from django.db import models
from django.conf import settings


class Employee(models.Model):
    TITLE_CHOICES = [
        ("대표이사",                  "대표이사"),
        ("Vice President, Sales",     "Vice President, Sales"),
        ("Sales Manager",             "Sales Manager"),
        ("Inside Sales Coordinator",  "Inside Sales Coordinator"),
        ("Sales Representative",      "Sales Representative"),
    ]

    employeeid = models.AutoField(primary_key=True)
    lastname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    department = models.CharField(max_length=40, blank=True, null=True)
    title = models.CharField(max_length=60, choices=TITLE_CHOICES, blank=True, null=True)
    titleofcourtesy = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    hiredate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=60,  blank=True, null=True)
    region = models.CharField(max_length=60,  blank=True, null=True)
    postalcode = models.CharField(max_length=20,  blank=True, null=True)
    country = models.CharField(max_length=60,  blank=True, null=True)
    homephone = models.CharField(max_length=40,  blank=True, null=True)
    extension = models.CharField(max_length=10,  blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reportsto = models.ForeignKey("self", on_delete=models.SET_NULL,
                blank=True, null=True, db_column="reportsto", related_name="reports") 
    photopath = models.CharField(max_length=200, blank=True, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employee',
    )

    class Meta:
        db_table = "employee"

    def __str__(self):
        return f"{self.lastname}{self.firstname}"


class EmployeeTerritory(models.Model):
    employeeid = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                    db_column="employeeid", related_name="territories")
    territoryid = models.ForeignKey("ssafy_international.Territory", on_delete=models.CASCADE,
                                    db_column="territoryid", related_name="employees")

    class Meta:
        db_table = "employeeterritory"
        unique_together = ("employeeid", "territoryid")


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('정상', '정상'),
        ('지각', '지각'),
        ('조퇴', '조퇴'),
        ('결근', '결근'),
        ('휴가', '휴가'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column="employeeid",
        related_name="attendances",
        verbose_name="직원",
    )
    date = models.DateField(db_column="date", verbose_name="날짜")
    checkin_time = models.TimeField(null=True, blank=True, db_column="checkin_time", verbose_name="출근 시간")
    checkout_time = models.TimeField(null=True, blank=True, db_column="checkout_time", verbose_name="퇴근 시간")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='정상', db_column="status", verbose_name="상태")
    note = models.CharField(max_length=200, blank=True, null=True, db_column="note", verbose_name="비고")

    class Meta:
        db_table = "attendance"
        unique_together = ("employee", "date")
        ordering = ["-date"]
        verbose_name = "근태"
        verbose_name_plural = "근태 목록"

    def __str__(self):
        return f"{self.employee} {self.date} ({self.status})"


class LeaveRequest(models.Model):
    TYPE_CHOICES = [
        ('연차', '연차'),
        ('병가', '병가'),
        ('경조사', '경조사'),
        ('기타', '기타'),
    ]
    STATUS_CHOICES = [
        ('대기', '대기'),
        ('승인', '승인'),
        ('반려', '반려'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, db_column="employeeid",
        related_name="leave_requests", verbose_name="신청자",
    )
    leave_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='연차', db_column="leave_type", verbose_name="휴가종류")
    start_date = models.DateField(db_column="start_date", verbose_name="시작일")
    end_date = models.DateField(db_column="end_date", verbose_name="종료일")
    days = models.DecimalField(max_digits=4, decimal_places=1, default=1, db_column="days", verbose_name="일수")
    reason = models.CharField(max_length=200, blank=True, null=True, db_column="reason", verbose_name="신청 사유")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='대기', db_column="status", verbose_name="상태")
    approver = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, db_column="approver_id",
        related_name="processed_leave_requests", verbose_name="처리자",
    )
    applied_at = models.DateTimeField(auto_now_add=True, db_column="applied_at", verbose_name="신청일시")
    processed_at = models.DateTimeField(null=True, blank=True, db_column="processed_at", verbose_name="처리일시")

    class Meta:
        db_table = "leaverequest"
        ordering = ["-applied_at"]
        verbose_name = "휴가 신청"
        verbose_name_plural = "휴가 신청 목록"

    def __str__(self):
        return f"{self.employee} {self.leave_type} {self.start_date}~{self.end_date} ({self.status})"


ANNUAL_LEAVE_DAYS = 15  # 연차 기준일수 (회사 정책 상수)