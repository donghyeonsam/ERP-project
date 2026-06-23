from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    path('channels/', views.channel_list),
    path('channels/<int:channel_id>/', views.channel_detail),
    path('channels/<int:channel_id>/messages/', views.channel_messages),
    path('channels/<int:channel_id>/read/', views.mark_channel_read),
    path('channels/<int:channel_id>/members/', views.add_channel_member),
    path('channels/<int:channel_id>/leave/', views.leave_channel),
    path('start-direct/', views.start_direct),
    path('messages/<int:message_id>/read/', views.mark_read),
]
