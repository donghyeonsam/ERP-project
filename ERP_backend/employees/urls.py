"""
employees/urls.py
- config 에서 path('api/v1/employees/', include('employees.urls')) 형태로 포함
- 'me/', 'org-chart/' 같은 고정 경로를 '<int:pk>/' 보다 위에 둬야 함
  (안 그러면 me/ 가 pk 로 잡혀서 충돌)
"""
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list),
    path('me/', views.employee_me),
    path('org-chart/', views.employee_org_chart),
    path('territories/', views.employee_territory_list),
    path('<int:pk>/', views.employee_detail),

    # 근태
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/today/', views.attendance_today, name='attendance_today'),
    path('attendance/admin/', views.attendance_admin_list, name='attendance_admin_list'),
    path('attendance/manual/', views.attendance_manual_create, name='attendance_manual_create'),
    path('attendance/<int:pk>/', views.attendance_detail, name='attendance_detail'),

    # 휴가
    path('leave-requests/', views.leave_request_list, name='leave_request_list'),
    path('leave-requests/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    path('leave-requests/<int:pk>/reject/', views.leave_request_reject, name='leave_request_reject'),
    path('leave-balances/', views.leave_balance_list, name='leave_balance_list'),
]