"""
messages/urls.py
- config 에서 path('api/v1/messages/', include('messages.urls')) 형태로 포함
"""
from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # 채널
    path('channels/', views.channel_list),
    path('channels/<int:channel_id>/', views.channel_detail),

    # 채널 메시지 (GET=폴링 조회, POST=작성)
    path('channels/<int:channel_id>/messages/', views.channel_messages),

    # DM 시작 (1:1 채널 찾기/생성)
    path('start-direct/', views.start_direct),

    # 메시지 읽음 처리
    path('messages/<int:message_id>/read/', views.mark_read),
]