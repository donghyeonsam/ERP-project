from django.urls import path
from . import views

urlpatterns = [
    # 1. CalendarEvent
    path('calendar-events/', views.calendar_event_list, name='calendar_event_list'),
    path('calendar-events/<int:pk>/', views.calendar_event_detail, name='calendar_event_detail'),

    # 2. Task
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),

    # 3. TaskComment
    path('task-comments/', views.task_comment_list, name='task_comment_list'),
    path('task-comments/<int:pk>/', views.task_comment_detail, name='task_comment_detail'),

    # 4. WorkNotification
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
]