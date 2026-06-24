from datetime import date, datetime, time, timedelta

from django.db import migrations

TODAY_OFFSET_TASKS = [
    (4, '거래처 분기 영업 보고서 작성', '영업1팀 분기 실적 보고서를 정리해 VP에게 제출', 'IN_PROGRESS', 'HIGH', 0),
    (4, '신규 거래처 계약서 검토', '법무팀 검토 의견 반영하여 계약서 최종안 확인', 'TODO', 'HIGH', -1),
    (4, '주간 영업 회의 준비', '이번 주 영업 실적 자료 정리', 'TODO', 'MEDIUM', 0),
    (4, '지난달 출장비 정산', '영수증 첨부하여 회계팀 제출', 'DONE', 'LOW', -3),
    (2, '영업1팀 월간 목표 검토', '팀별 달성률 점검 및 차월 목표 조정', 'TODO', 'HIGH', 0),
    (2, '신규 거래처 승인 검토', '영업팀에서 올린 신규 거래처 등록 승인 여부 결정', 'IN_PROGRESS', 'MEDIUM', 0),
]

TODAY_OFFSET_EVENTS = [
    (4, '거래처 미팅', '(주)한국프레시 신규 계약 논의', 14, 0, 1),
    (2, '영업1팀 주간 회의', '주간 실적 점검 및 이슈 공유', 10, 0, 1),
]


def seed(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    Task = apps.get_model("works", "Task")
    CalendarEvent = apps.get_model("works", "CalendarEvent")

    titles = [t[1] for t in TODAY_OFFSET_TASKS]
    if Task.objects.filter(title__in=titles).exists():
        return

    today = date.today()
    for emp_id, title, content, status, priority, offset in TODAY_OFFSET_TASKS:
        emp = Employee.objects.filter(pk=emp_id).first()
        if not emp:
            continue
        due = today + timedelta(days=offset)
        Task.objects.create(
            assignee=emp, creator=emp, title=title, content=content,
            status=status, priority=priority, due_date=due,
        )

    for emp_id, title, description, hour, minute, duration in TODAY_OFFSET_EVENTS:
        emp = Employee.objects.filter(pk=emp_id).first()
        if not emp:
            continue
        start = datetime.combine(today, time(hour, minute))
        end = start + timedelta(hours=duration)
        CalendarEvent.objects.create(
            employee=emp, title=title, description=description,
            start_time=start, end_time=end, event_type='MANUAL',
        )


def unseed(apps, schema_editor):
    Task = apps.get_model("works", "Task")
    CalendarEvent = apps.get_model("works", "CalendarEvent")
    Task.objects.filter(title__in=[t[1] for t in TODAY_OFFSET_TASKS]).delete()
    CalendarEvent.objects.filter(title__in=[e[1] for e in TODAY_OFFSET_EVENTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("works", "0002_seed_demo_tasks"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
