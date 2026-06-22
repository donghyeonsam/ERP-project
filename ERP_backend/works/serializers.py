from rest_framework import serializers
from .models import CalendarEvent, Task, TaskComment, WorkNotification

# =====================================================================
# 1. CalendarEvent (캘린더 일정) Serializer
# =====================================================================
class CalendarEventSerializer(serializers.ModelSerializer):
    # Vue 화면에서 어떤 직원의 일정인지 이름을 바로 보여주기 위한 필드
    employee_name = serializers.CharField(source='employee.lastname', read_only=True)

    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'employee', 'employee_name', 'title', 'description',
            'start_time', 'end_time', 'color', 'event_type', 'is_all_day'
        ]


# =====================================================================
# 2. TaskComment (업무 댓글) Serializer
# =====================================================================
class TaskCommentSerializer(serializers.ModelSerializer):
    # 댓글 작성자의 이름을 바로 매칭 (예: "홍길동")
    employee_name = serializers.CharField(source='employee.lastname', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'employee', 'employee_name', 'comment', 'created_at']


# =====================================================================
# 3. Task (할 일 / 업무 마스터) Serializer
# =====================================================================
class TaskSerializer(serializers.ModelSerializer):
    # 중요: 업무 조회 시 하위 댓글 목록(comments)을 리스트로 묶어서 함께 포함시킴
    # models.py에서 설정한 related_name="comments"와 변수명이 일치해야 합니다.
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    # 가독성을 위해 담당자와 지시자의 이름을 문자열로 추가
    assignee_name = serializers.CharField(source='assignee.lastname', read_only=True)
    creator_name = serializers.CharField(source='creator.lastname', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'assignee', 'assignee_name', 'creator', 'creator_name',
            'title', 'content', 'status', 'priority', 'due_date',
            'is_ai_recommended', 'reference_target',
            'created_at', 'updated_at', 'completed_at', 'comments'
        ]


# =====================================================================
# 4. WorkNotification (실시간 업무 알림) Serializer
# =====================================================================
class WorkNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkNotification
        fields = '__all__'