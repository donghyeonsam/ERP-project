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
    path('attendance/<int:pk>/', views.attendance_detail, name='attendance_detail'),
]