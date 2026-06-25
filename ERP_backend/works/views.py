import json
import re
from datetime import date, datetime, timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

from .models import CalendarEvent, Task, TaskComment, WorkNotification, Memo
from .serializers import (
    CalendarEventSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    WorkNotificationSerializer,
    MemoSerializer,
)
from employees.views import current_employee


def _week_range(target_date):
    """target_date가 속한 주(일~토)의 날짜 리스트 7개를 반환한다."""
    days_since_sunday = (target_date.weekday() + 1) % 7  # Python weekday: Mon=0..Sun=6
    week_start = target_date - timedelta(days=days_since_sunday)
    return [week_start + timedelta(days=i) for i in range(7)]


def _invalidate_ai_cache(employee_id, dates):
    """해당 직원의 AI 추천 캐시를 지정된 날짜가 포함된 주(일~토) 전체에 대해 무효화한다.
    Task/CalendarEvent가 생성·수정·삭제될 때마다 호출해, 워크플로우 페이지가
    최신 데이터로 즉시 재계산되도록 한다. AI 추천이 '해당 날짜가 속한 주간 마감 업무'를
    함께 분석하므로, 그 주의 어느 날짜를 보고 있었든 캐시가 무효화되어야 한다."""
    if not employee_id:
        return
    for d in dates:
        if not d:
            continue
        target = d if isinstance(d, date) else datetime.strptime(d, '%Y-%m-%d').date()
        for day in _week_range(target):
            cache.delete(f'ai_recommend:{employee_id}:{day.isoformat()}')


# =====================================================================
# 1. CalendarEvent (캘린더 일정)
# =====================================================================
@api_view(['GET', 'POST'])
def calendar_event_list(request):
    if request.method == 'GET':
        # 직원마다 자신의 일정만 보이도록 필터링 (전체 직원 일정을 공유하던 기존 버그 수정)
        emp = current_employee(request)
        events = CalendarEvent.objects.filter(employee=emp).select_related('employee')
        serializer = CalendarEventSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CalendarEventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event = serializer.save()
            event_date = event.start_time.date().isoformat() if event.start_time else None
            _invalidate_ai_cache(event.employee_id, {date.today().isoformat(), event_date})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def calendar_event_detail(request, pk):
    emp = current_employee(request)
    event = get_object_or_404(CalendarEvent.objects.select_related('employee').filter(employee=emp), pk=pk)

    if request.method == 'GET':
        serializer = CalendarEventSerializer(event)
        return Response(serializer.data)

    elif request.method == 'PUT':
        old_date = event.start_time.date().isoformat() if event.start_time else None
        serializer = CalendarEventSerializer(event, data=request.data)
        if serializer.is_valid(raise_exception=True):
            updated = serializer.save()
            new_date = updated.start_time.date().isoformat() if updated.start_time else None
            _invalidate_ai_cache(updated.employee_id, {date.today().isoformat(), old_date, new_date})
            return Response(serializer.data)

    elif request.method == 'DELETE':
        event_date = event.start_time.date().isoformat() if event.start_time else None
        _invalidate_ai_cache(event.employee_id, {date.today().isoformat(), event_date})
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. Task (할 일 / 업무 마스터)
# =====================================================================
@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        # 직원마다 자신이 담당(assignee)하거나 지시(creator)한 업무만 보이도록 필터링
        # (전체 직원의 업무가 한 화면에 공유되어 보이던 기존 버그 수정)
        emp = current_employee(request)
        tasks = Task.objects.filter(
            Q(assignee=emp) | Q(creator=emp)
        ).distinct().prefetch_related('comments').select_related('assignee', 'creator')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            task = serializer.save()
            due = task.due_date.isoformat() if task.due_date else None
            _invalidate_ai_cache(task.assignee_id, {date.today().isoformat(), due})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail(request, pk):
    emp = current_employee(request)
    task = get_object_or_404(
        Task.objects.prefetch_related('comments').select_related('assignee', 'creator').filter(
            Q(assignee=emp) | Q(creator=emp)
        ),
        pk=pk
    )

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        old_due = task.due_date.isoformat() if task.due_date else None
        old_assignee = task.assignee_id
        serializer = TaskSerializer(task, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid(raise_exception=True):
            updated = serializer.save()
            new_due = updated.due_date.isoformat() if updated.due_date else None
            dates = {date.today().isoformat(), old_due, new_due}
            _invalidate_ai_cache(old_assignee, dates)
            if updated.assignee_id != old_assignee:
                _invalidate_ai_cache(updated.assignee_id, dates)
            return Response(serializer.data)

    elif request.method == 'DELETE':
        due = task.due_date.isoformat() if task.due_date else None
        _invalidate_ai_cache(task.assignee_id, {date.today().isoformat(), due})
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 3. TaskComment (업무 댓글)
# =====================================================================
@api_view(['GET', 'POST'])
def task_comment_list(request):
    if request.method == 'GET':
        # ?task=<id> 쿼리파라미터로 해당 업무의 댓글만 필터링 (프론트는 이를 기대하지만 기존 코드는
        # 무시하고 전체 댓글을 반환하던 버그였음). 동시에 자신이 담당/지시한 업무의 댓글만 보이도록 제한.
        emp = current_employee(request)
        comments = TaskComment.objects.select_related('employee', 'task').filter(
            Q(task__assignee=emp) | Q(task__creator=emp)
        )
        task_id = request.query_params.get('task')
        if task_id:
            comments = comments.filter(task_id=task_id)
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def task_comment_detail(request, pk):
    emp = current_employee(request)
    comment = get_object_or_404(
        TaskComment.objects.select_related('employee').filter(Q(task__assignee=emp) | Q(task__creator=emp)),
        pk=pk
    )
    
    if request.method == 'GET':
        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = TaskCommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 4. WorkNotification (실시간 업무 알림)
# =====================================================================
@api_view(['GET', 'POST'])
def notification_list(request):
    if request.method == 'GET':
        # 본인 수신 알림만 보이도록 필터링 (전체 직원 알림이 공유되어 보이던 기존 버그 수정)
        emp = current_employee(request)
        notifications = WorkNotification.objects.filter(employee=emp)
        serializer = WorkNotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WorkNotificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def notification_detail(request, pk):
    emp = current_employee(request)
    notification = get_object_or_404(WorkNotification, pk=pk, employee=emp)
    
    if request.method == 'GET':
        serializer = WorkNotificationSerializer(notification)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = WorkNotificationSerializer(notification, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 5. Memo (개인 메모)
# =====================================================================
@api_view(['GET', 'POST'])
def memo_list(request):
    emp = current_employee(request)
    if emp is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        memos = Memo.objects.filter(employee=emp)
        return Response(MemoSerializer(memos, many=True).data)

    serializer = MemoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(employee=emp)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def memo_detail(request, pk):
    emp = current_employee(request)
    memo = get_object_or_404(Memo, pk=pk, employee=emp)

    if request.method == 'GET':
        return Response(MemoSerializer(memo).data)

    if request.method == 'PUT':
        serializer = MemoSerializer(memo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    memo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 6. AI 추천 워크플로우 — 해당 날짜의 업무/일정/주문/발주를 모아 OpenAI로 우선순위 추천
# =====================================================================
def _parse_date_param(request):
    date_str = request.query_params.get('date') or date.today().isoformat()
    try:
        return date_str, datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return date_str, None


def _gather_work_items(emp, target_date):
    """현재 직원의 해당 날짜 업무 후보를 모아 type-agnostic한 dict 리스트로 정규화한다.
    각 항목은 source_type:source_id 조합으로 식별되며, 완료 처리 시 이 정보로
    원본 레코드(Task/Order/PurchaseOrder)를 갱신한다."""
    from ssafy_international.models import Order
    from procurement.models import PurchaseOrder

    items = []

    # 당일 마감 업무만 보던 것을 target_date가 속한 주(일~토) 전체 마감 업무로 확장.
    # AI가 그 주간 업무 전체의 중요도를 분석해 우선순위를 매길 수 있도록 데이터 범위를 넓힌다.
    week_days = _week_range(target_date)
    week_start, week_end = week_days[0], week_days[-1]
    tasks = Task.objects.filter(assignee=emp).filter(
        Q(due_date__range=(week_start, week_end)) | Q(due_date__lt=week_start, status__in=['TODO', 'IN_PROGRESS'])
    )
    for t in tasks:
        items.append({
            'source_type': 'task', 'source_id': t.id,
            'title': t.title, 'type': '업무', 'detail': t.content,
            'status': t.status, 'done': t.status == 'DONE',
            'deadline': t.due_date.isoformat() if t.due_date else None,
            'priority_hint': t.priority,
        })

    events = CalendarEvent.objects.filter(employee=emp, start_time__date=target_date)
    for e in events:
        items.append({
            'source_type': 'calendar', 'source_id': e.id,
            'title': e.title, 'type': '일정', 'detail': e.description,
            'status': '예정', 'done': False,
            'deadline': e.start_time.isoformat() if e.start_time else None,
            'priority_hint': None,
        })

    orders = Order.objects.filter(employeeid=emp, requireddate__date=target_date)
    for o in orders:
        items.append({
            'source_type': 'order', 'source_id': o.orderid,
            'title': f'주문 #{o.orderid} 배송 처리', 'type': '주문배송',
            'detail': f'거래처: {o.shipname or o.customerid_id}',
            'status': '배송완료' if o.shippeddate else '배송대기', 'done': bool(o.shippeddate),
            'deadline': o.requireddate.isoformat() if o.requireddate else None,
            'priority_hint': None,
        })

    pos = PurchaseOrder.objects.filter(employeeid=emp, expecteddate=target_date)
    for po in pos:
        items.append({
            'source_type': 'purchase_order', 'source_id': po.id,
            'title': f'발주 #{po.id} 입고 처리', 'type': '발주입고',
            'detail': f'공급업체 ID: {po.supplierid_id}',
            'status': po.status, 'done': po.status == 'received',
            'deadline': po.expecteddate.isoformat() if po.expecteddate else None,
            'priority_hint': None,
        })

    return items


def _call_ai_ranking(raw_items, date_str, week_start, week_end):
    from openai import OpenAI
    client = OpenAI(api_key=settings.GMS_KEY, base_url=settings.GMS_BASE_URL)

    task_data = json.dumps(
        [{**it, 'id': f"{it['source_type']}:{it['source_id']}"} for it in raw_items],
        ensure_ascii=False,
    )
    system_msg = "You are an ERP workflow assistant. Return only a valid JSON array, no other text."
    user_msg = (
        f"The reference date is {date_str}, which falls in the calendar week {week_start} (Sun) to {week_end} (Sat).\n"
        "The item list below includes work items due anywhere within that week (plus older overdue items). "
        "Analyze each item's importance using its own 'deadline' field and return a JSON array ordered most-to-least urgent.\n"
        "Each element must follow this shape exactly:\n"
        '{"id": <original record id, copied verbatim>, "title": <task title>, "type": <task type string>, '
        '"priority": "high" | "medium" | "low", "deadline": <ISO date string or null>, '
        '"status": <current status string>, "summary": <one-sentence description>, '
        '"suggested_order": <integer starting at 1>, "ai_reason": <one sentence explaining this item\'s placement>}\n'
        "Priority rules:\n"
        f"- Deadline is {date_str} (today) or already overdue -> high\n"
        "- Deadline falls later this week -> medium, ranked sooner-deadline-first\n"
        "- In-progress items before not-started items of the same priority\n"
        "- Completed / approved / delivered items -> listed last, marked done\n"
        f"Task data: {task_data}\n"
        "Write title/summary/ai_reason values in Korean."
    )

    completion = client.chat.completions.create(
        model=settings.GMS_MODEL,
        messages=[
            {"role": "developer", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )
    text = completion.choices[0].message.content.strip()
    text = re.sub(r'^```[a-zA-Z]*\n?|\n?```$', '', text.strip())
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError('AI response is not a list')
    data.sort(key=lambda it: it.get('suggested_order') or 999)
    return data


@api_view(['GET'])
def ai_recommend(request):
    emp = current_employee(request)
    if emp is None:
        return Response({'error': '사원 정보를 찾을 수 없습니다.', 'items': []}, status=status.HTTP_403_FORBIDDEN)

    date_str, target_date = _parse_date_param(request)
    if target_date is None:
        return Response({'error': '날짜 형식이 올바르지 않습니다.', 'items': []}, status=status.HTTP_400_BAD_REQUEST)

    cache_key = f'ai_recommend:{emp.employeeid}:{date_str}'
    force = request.query_params.get('force') == '1'
    cached = None if force else cache.get(cache_key)
    if cached is not None:
        return Response(cached)

    raw_items = _gather_work_items(emp, target_date)
    if not raw_items:
        result = {'error': None, 'items': []}
        cache.set(cache_key, result, 60)
        return Response(result)

    if not settings.GMS_KEY:
        print('[ai_recommend] GMS_KEY가 설정되어 있지 않아 AI 추천을 건너뜁니다. ERP_backend/.env 를 확인하세요.')
        return Response({'error': 'AI unavailable', 'items': []})

    try:
        week_days = _week_range(target_date)
        ranked = _call_ai_ranking(raw_items, date_str, week_days[0].isoformat(), week_days[-1].isoformat())
        # AI 응답 스키마에는 done이 없으므로, 원본 데이터의 done 플래그를 id 기준으로 다시 병합한다
        raw_by_id = {f"{it['source_type']}:{it['source_id']}": it for it in raw_items}
        for item in ranked:
            raw = raw_by_id.get(item.get('id'))
            item['done'] = bool(raw['done']) if raw else False
        result = {'error': None, 'items': ranked}
        cache.set(cache_key, result, 60)
        return Response(result)
    except Exception as e:
        print(f'[ai_recommend] OpenAI 호출/파싱 실패: {e}')
        return Response({'error': 'AI unavailable', 'items': []})


@api_view(['GET'])
def status_summary(request):
    emp = current_employee(request)
    if emp is None:
        return Response({'items': []}, status=status.HTTP_403_FORBIDDEN)

    date_str, target_date = _parse_date_param(request)
    if target_date is None:
        return Response({'items': []}, status=status.HTTP_400_BAD_REQUEST)

    raw_items = _gather_work_items(emp, target_date)
    summary = [
        {'id': f"{it['source_type']}:{it['source_id']}", 'status': it['status'], 'done': it['done']}
        for it in raw_items
    ]
    return Response({'items': summary})