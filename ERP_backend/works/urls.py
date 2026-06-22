from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF 라우터 초기화
router = DefaultRouter()

# 각각의 ViewSet을 URL 엔드포인트에 등록
router.register(r'calendar-events', views.CalendarEventViewSet, basename='calendarevent')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'task-comments', views.TaskCommentViewSet, basename='taskcomment')
router.register(r'notifications', views.WorkNotificationViewSet, basename='worknotification')

# 최종 API 주소 자동 매핑
urlpatterns = [
    path('', include(router.urls)),
]