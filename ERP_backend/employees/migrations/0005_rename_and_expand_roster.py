from datetime import date

from django.db import migrations

# 기존 10명 중 대표이사(10)·이민석(4)은 그대로 유지하고, 나머지 8명은
# 이름만 변경한다 (pk/title/level/reportsto/department는 그대로 유지).
RENAMES = {
    1: ("이", "지은"),
    2: ("김", "현성"),  # 김현성 = VP(레벨4) 유지
    3: ("백", "현지"),
    5: ("이", "성훈"),
    6: ("신", "건우"),
    7: ("신", "혜민"),
    8: ("정", "현지"),
    9: ("정", "지훈"),
}

# 신규 9명 — 영업3팀(정예은 신설팀) + 기존 영업1팀/영업2팀 보강
NEW_EMPLOYEES = [
    # (lastname, firstname, title, reportsto_id(기존 직원 기준, 정예은은 별도 처리), department, hiredate)
    ("정", "예은", "Sales Manager", 2, "영업3팀", date(2018, 3, 2)),
    ("박", "도현", "Inside Sales Coordinator", 2, "영업1팀", date(2019, 6, 1)),
    ("황", "승준", "Inside Sales Coordinator", 2, "영업1팀", date(2020, 1, 15)),
    ("김", "도아", "Sales Representative", 5, "영업2팀", date(2019, 9, 10)),
    ("이", "성빈", "Sales Representative", 5, "영업2팀", date(2020, 4, 20)),
    ("신", "하림", "Sales Representative", 5, "영업2팀", date(2021, 2, 1)),
]
# 정예은 산하로 들어갈 신규 팀원 (정예은의 employeeid는 마이그레이션 실행 시 동적으로 결정)
NEW_TEAM3_MEMBERS = [
    ("류", "은혜", "Sales Representative", "영업3팀", date(2019, 11, 5)),
    ("이", "준우", "Sales Representative", "영업3팀", date(2020, 7, 18)),
    ("이", "성현", "Sales Representative", "영업3팀", date(2021, 5, 30)),
]


def migrate_forward(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")

    for emp_id, (lastname, firstname) in RENAMES.items():
        Employee.objects.filter(pk=emp_id).update(lastname=lastname, firstname=firstname)

    for lastname, firstname, title, reportsto_id, department, hiredate in NEW_EMPLOYEES:
        Employee.objects.create(
            lastname=lastname, firstname=firstname, title=title,
            reportsto_id=reportsto_id, department=department, hiredate=hiredate,
        )

    jeong_yeeun = Employee.objects.get(lastname="정", firstname="예은")
    for lastname, firstname, title, department, hiredate in NEW_TEAM3_MEMBERS:
        Employee.objects.create(
            lastname=lastname, firstname=firstname, title=title,
            reportsto_id=jeong_yeeun.employeeid, department=department, hiredate=hiredate,
        )


def migrate_backward(apps, schema_editor):
    # 이름 변경은 원래 이름을 보존하지 않았으므로 역방향 복원은 지원하지 않음(신규 레코드만 제거)
    Employee = apps.get_model("employees", "Employee")
    names = set()
    for lastname, firstname, *_ in NEW_EMPLOYEES:
        names.add((lastname, firstname))
    for lastname, firstname, *_ in NEW_TEAM3_MEMBERS:
        names.add((lastname, firstname))
    for lastname, firstname in names:
        Employee.objects.filter(lastname=lastname, firstname=firstname).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0004_seed_department_and_leave"),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
    ]
