"""
employees/views.py
- Employee(self-FK reportsto), EmployeeTerritory
- 역할 레벨은 DB에 저장하지 않고 title → level 로 "코드에서" 매핑한다.
- TITLE_LEVEL / get_level / current_employee 는 messages 앱 등에서도 import 해서 쓴다.
  (이상적으로는 employees/permissions.py 같은 별도 모듈로 빼도 좋지만,
   지금은 views 에 함께 둔다.)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Employee, EmployeeTerritory, Attendance
from .serializers import EmployeeSerializer, EmployeeTerritorySerializer, AttendanceSerializer


# ---------------------------------------------------------------------
# 역할 레벨 매핑 (DB에 저장하지 않고 코드에서 결정)
# ---------------------------------------------------------------------
TITLE_LEVEL = {
    '대표이사': 5,
    'Vice President, Sales': 4,
    'Sales Manager': 3,
    'Inside Sales Coordinator': 2,
    'Sales Representative': 1,
}


def get_level(employee):
    """Employee 객체 → 역할 레벨 (매핑에 없으면 0)"""
    if employee is None:
        return 0
    return TITLE_LEVEL.get(employee.title, 0)


def current_employee(request):
    """
    로그인한 JWT 사용자(request.user) ↔ Employee 연결.
    정상 등록 경로: EmployeeRegisterSerializer.custom_signup 에서 Employee.user 연결.
    폴백: user와 연결된 Employee가 없으면 최소 Employee 레코드를 자동 생성한다.
    (슈퍼유저·테스트 계정 등 정식 등록 절차를 거치지 않은 계정 대비)
    """
    emp = getattr(request.user, 'employee', None)
    if emp is None:
        username = getattr(request.user, 'username', None) or 'user'
        emp, _ = Employee.objects.get_or_create(
            user=request.user,
            defaults={
                'lastname': username[:1],
                'firstname': username[1:] if len(username) > 1 else username,
            },
        )
    return emp


# =====================================================================
# Employee — 전체 CRUD
# =====================================================================
@api_view(['GET', 'POST'])
def employee_list(request):
    if request.method == 'GET':
        qs = Employee.objects.all()
        # 예: ?title=Sales Manager 로 직책 필터 (선택)
        title = request.query_params.get('title')
        if title:
            qs = qs.filter(title=title)
        return Response(EmployeeSerializer(qs, many=True).data)

    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def employee_detail(request, pk):
    obj = get_object_or_404(Employee, pk=pk)

    if request.method == 'GET':
        data = EmployeeSerializer(obj).data
        data['level'] = get_level(obj)   # 코드 매핑 레벨도 함께 내려줌
        return Response(data)

    if request.method == 'PUT':
        serializer = EmployeeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# me — 로그인한 사용자 본인의 사원 정보 + 레벨 (프론트 권한 분기용)
# =====================================================================
@api_view(['GET'])
def employee_me(request):
    emp = current_employee(request)
    if emp is None:
        return Response(
            {'detail': '로그인 계정과 연결된 사원 정보가 없습니다.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    data = EmployeeSerializer(emp).data
    data['level'] = get_level(emp)
    return Response(data)


# =====================================================================
# org-chart — reportsto(self-FK) 로 조직도 트리 생성
# =====================================================================
@api_view(['GET'])
def employee_org_chart(request):
    employees = Employee.objects.all()

    # 1) employeeid → 노드 dict
    nodes = {}
    for e in employees:
        nodes[e.employeeid] = {
            'employeeid': e.employeeid,
            'name': f'{e.lastname}{e.firstname}',  # 한국식: 성 + 이름 (예: 김동현)
            'title': e.title,
            'level': get_level(e),
            'reports': [],   # 부하 직원들
        }

    # 2) reportsto 로 부모-자식 연결
    roots = []
    for e in employees:
        node = nodes[e.employeeid]
        manager_id = e.reportsto_id   # raw FK id (None 이면 최상위)
        if manager_id and manager_id in nodes:
            nodes[manager_id]['reports'].append(node)
        else:
            roots.append(node)        # 상사가 없으면 루트(대표이사 등)

    return Response(roots)


# =====================================================================
# EmployeeTerritory — 사원-담당구역 매핑 (조회/생성)
# =====================================================================
@api_view(['GET', 'POST'])
def employee_territory_list(request):
    if request.method == 'GET':
        qs = EmployeeTerritory.objects.all()
        employeeid = request.query_params.get('employeeid')
        if employeeid:
            qs = qs.filter(employeeid=employeeid)
        return Response(EmployeeTerritorySerializer(qs, many=True).data)

    serializer = EmployeeTerritorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================
# Attendance — 근태 CRUD
# =====================================================================
@api_view(['GET', 'POST'])
def attendance_list(request):
    emp = current_employee(request)
    if emp is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        qs = Attendance.objects.filter(employee=emp).order_by('-date')
        # ?month=2026-06 형태로 월별 필터
        month = request.query_params.get('month')
        if month:
            try:
                year, m = month.split('-')
                qs = qs.filter(date__year=int(year), date__month=int(m))
            except ValueError:
                pass
        return Response(AttendanceSerializer(qs, many=True).data)

    # POST: 오늘 근태 레코드 생성(없으면) 또는 체크인 처리
    from django.utils import timezone
    import datetime
    today = timezone.localdate()

    data = request.data.copy()
    data['employee'] = emp.pk
    if 'date' not in data:
        data['date'] = str(today)

    # 이미 오늘 레코드가 있으면 기존 객체 반환 (중복 방지)
    obj, created = Attendance.objects.get_or_create(
        employee=emp,
        date=data['date'],
        defaults={'checkin_time': data.get('checkin_time'), 'status': data.get('status', '정상')}
    )
    if not created and data.get('checkin_time') and not obj.checkin_time:
        obj.checkin_time = data['checkin_time']
        obj.save()
    return Response(AttendanceSerializer(obj).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
def attendance_today(request):
    """오늘 날짜 근태 조회 / 업데이트 (출근·퇴근 시간 기록용)"""
    emp = current_employee(request)
    if emp is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    from django.utils import timezone
    today = timezone.localdate()
    obj, _ = Attendance.objects.get_or_create(employee=emp, date=today)

    if request.method == 'GET':
        return Response(AttendanceSerializer(obj).data)

    serializer = AttendanceSerializer(obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def attendance_detail(request, pk):
    emp = current_employee(request)
    obj = get_object_or_404(Attendance, pk=pk, employee=emp)

    if request.method == 'GET':
        return Response(AttendanceSerializer(obj).data)

    if request.method == 'PUT':
        serializer = AttendanceSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)