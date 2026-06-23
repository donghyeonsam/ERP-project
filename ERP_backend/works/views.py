from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404

from .models import CalendarEvent, Task, TaskComment, WorkNotification
from .serializers import (
    CalendarEventSerializer,
    TaskSerializer,
    TaskCommentSerializer,
    WorkNotificationSerializer
)

# =====================================================================
# 1. CalendarEvent (캘린더 일정)
# =====================================================================
@api_view(['GET', 'POST'])
def calendar_event_list(request):
    if request.method == 'GET':
        events = CalendarEvent.objects.all().select_related('employee')
        serializer = CalendarEventSerializer(events, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = CalendarEventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def calendar_event_detail(request, pk):
    event = get_object_or_404(CalendarEvent.objects.select_related('employee'), pk=pk)
    
    if request.method == 'GET':
        serializer = CalendarEventSerializer(event)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = CalendarEventSerializer(event, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 2. Task (할 일 / 업무 마스터)
# =====================================================================
@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        # 하위 댓글(comments)과 담당자 정보를 효율적으로 JOIN
        tasks = Task.objects.all().prefetch_related('comments').select_related('assignee', 'creator')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    task = get_object_or_404(
        Task.objects.prefetch_related('comments').select_related('assignee', 'creator'), 
        pk=pk
    )
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            
    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# 3. TaskComment (업무 댓글)
# =====================================================================
@api_view(['GET', 'POST'])
def task_comment_list(request):
    if request.method == 'GET':
        comments = TaskComment.objects.all().select_related('employee')
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def task_comment_detail(request, pk):
    comment = get_object_or_404(TaskComment.objects.select_related('employee'), pk=pk)
    
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
        notifications = WorkNotification.objects.all()
        serializer = WorkNotificationSerializer(notifications, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = WorkNotificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def notification_detail(request, pk):
    notification = get_object_or_404(WorkNotification, pk=pk)
    
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