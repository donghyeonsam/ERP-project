from django.shortcuts import render

from rest_framework import viewsets
from .models import CalendarEvent, Task, TaskComment, WorkNotification
from .serializers import (
    CalendarEventSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    WorkNotificationSerializer
)

# =====================================================================
# 1. CalendarEvent (캘린더 일정) ViewSet
# =====================================================================
class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all().select_related('employee')
    serializer_class = CalendarEventSerializer


# =====================================================================
# 2. Task (할 일 / 업무 마스터) ViewSet
# =====================================================================
class TaskViewSet(viewsets.ModelViewSet):
    # 하위 댓글(comments)과 담당자 정보를 N+1 문제 없이 효율적으로 JOIN하여 가져옵니다.
    queryset = Task.objects.all().prefetch_related('comments').select_related('assignee', 'creator')
    serializer_class = TaskSerializer


# =====================================================================
# 3. TaskComment (업무 댓글) ViewSet
# =====================================================================
class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.all().select_related('employee')
    serializer_class = TaskCommentSerializer


# =====================================================================
# 4. WorkNotification (실시간 업무 알림) ViewSet
# =====================================================================
class WorkNotificationViewSet(viewsets.ModelViewSet):
    queryset = WorkNotification.objects.all()
    serializer_class = WorkNotificationSerializer