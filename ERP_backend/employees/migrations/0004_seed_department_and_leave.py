from datetime import date, timedelta

from django.db import migrations

# 실제 조직(reportsto) 구조 기준 부서 배정 — 생산/연구개발 인력이 없는 영업 중심 조직이라
# 참고 화면의 부서명 중 실제로 존재하는 인력에 맞는 것만 사용한다.
DEPARTMENT_MAP = {
    10: '경영지원부',  # 대표이사
    2: '영업1팀', 3: '영업1팀', 4: '영업1팀', 8: '영업1팀', 1: '영업1팀',
    5: '영업2팀', 6: '영업2팀', 7: '영업2팀', 9: '영업2팀',
}

LEAVE_SEED = [
    # (employeeid, leave_type, start_offset_days, length_days, status, reason)
    (1, '연차', -20, 2, '승인', '가족 여행'),
    (3, '연차', -15, 1, '승인', '개인 사정'),
    (6, '병가', -10, 1, '승인', '병원 진료'),
    (7, '연차', -5, 3, '대기', '여름 휴가'),
    (9, '경조사', -3, 2, '대기', '가족 경조사'),
    (4, '연차', -30, 1, '반려', '연차 소진 초과'),
]


def seed(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    LeaveRequest = apps.get_model("employees", "LeaveRequest")

    for eid, dept in DEPARTMENT_MAP.items():
        Employee.objects.filter(pk=eid).update(department=dept)

    if LeaveRequest.objects.exists():
        return

    today = date.today()
    for eid, ltype, offset, length, status, reason in LEAVE_SEED:
        try:
            emp = Employee.objects.get(pk=eid)
        except Employee.DoesNotExist:
            continue
        start = today + timedelta(days=offset)
        end = start + timedelta(days=length - 1)
        LeaveRequest.objects.create(
            employee=emp, leave_type=ltype, start_date=start, end_date=end,
            days=length, reason=reason, status=status,
            approver=Employee.objects.filter(pk=2).first() if status != '대기' else None,
        )


def unseed(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    LeaveRequest = apps.get_model("employees", "LeaveRequest")
    LeaveRequest.objects.all().delete()
    Employee.objects.filter(pk__in=DEPARTMENT_MAP.keys()).update(department=None)


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0003_employee_department_leaverequest"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
