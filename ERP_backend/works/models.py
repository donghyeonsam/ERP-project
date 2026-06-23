
# Create your models here.
from django.db import models

class CalendarEvent(models.Model):
    id = models.AutoField(primary_key=True, db_column="id", verbose_name="이벤트 ID")
    
    # 이 일정을 등록한 직원 연결
    employee = models.ForeignKey(
        "employees.Employee", 
        on_delete=models.CASCADE, 
        db_column="employeeid", 
        related_name="calendar_events",
        verbose_name="담당 직원"
    )
    
    title = models.CharField(max_length=150, db_column="title", verbose_name="일정 제목")
    description = models.TextField(blank=True, null=True, db_column="description", verbose_name="상세 내용")
    
    # FullCalendar 등 프론트 라이브러리 연동용 글로벌 표준 포맷
    start_time = models.DateTimeField(db_column="starttime", verbose_name="시작 일시")
    end_time = models.DateTimeField(db_column="endtime", verbose_name="종료 일시")
    
    # 캘린더 화면에서 카테고리별 색상 구분을 위함 (예: #3788D8)
    color = models.CharField(max_length=7, default="#3788D8", db_column="color", verbose_name="색상 코드")
    
    # 이벤트 소스 구분 (MANUAL: 직접등록, SYSTEM: 재무 만기알림 등 시스템 자동 등록)
    event_type = models.CharField(max_length=30, default="MANUAL", db_column="eventtype", verbose_name="이벤트 유형")
    
    is_all_day = models.BooleanField(default=False, db_column="isallday", verbose_name="종일 일정 여부")

    class Meta:
        db_table = "calendarevent"
        verbose_name = "캘린더 일정"
        verbose_name_plural = "캘린더 일정 목록"

    def __str__(self):
        return f"[{self.employee.lastname}{self.employee.firstname}] {self.title}"


class Task(models.Model):
    id = models.AutoField(primary_key=True, db_column="id", verbose_name="업무 ID")
    
    # 이 업무를 책임지고 처리해야 하는 담당 사원
    assignee = models.ForeignKey(
        "employees.Employee", 
        on_delete=models.CASCADE, 
        db_column="assignee_id", 
        related_name="assigned_tasks",
        verbose_name="담당자"
    )
    
    # 업무를 생성하거나 지시한 사람 (상사 혹은 시스템봇 등)
    creator = models.ForeignKey(
        "employees.Employee", 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        db_column="creator_id", 
        related_name="created_tasks",
        verbose_name="지시자/생성자"
    )
    
    title = models.CharField(max_length=150, db_column="title", verbose_name="업무명")
    content = models.TextField(db_column="content", verbose_name="업무 내용")
    
    # 칸반 보드 렌더링용 진행 상태 (TODO, IN_PROGRESS, DONE)
    status = models.CharField(max_length=20, default="TODO", db_column="status", verbose_name="진행 상태")
    # 우선순위 (HIGH, MEDIUM, LOW)
    priority = models.CharField(max_length=10, default="MEDIUM", db_column="priority", verbose_name="우선순위")
    
    # 업무 마감 기한
    due_date = models.DateField(blank=True, null=True, db_column="duedate", verbose_name="마감 기한")
    
    # [추천사항 1] AI 기반 워크플로우 연동을 위한 피처
    is_ai_recommended = models.BooleanField(default=False, db_column="is_ai_recommended", verbose_name="AI 추천 여부")
    # AI가 이 태스크를 제안한 근거 도메인 타겟 (예: "productcost:5", "accountsreceivable:102")
    reference_target = models.CharField(max_length=50, blank=True, null=True, db_column="reference_target", verbose_name="참조 데이터 소스")

    created_at = models.DateTimeField(auto_now_add=True, db_column="createdat", verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, db_column="updatedat", verbose_name="수정 일시")
    completed_at = models.DateTimeField(blank=True, null=True, db_column="completedat", verbose_name="완료 일시")

    class Meta:
        db_table = "task"
        verbose_name = "할 일(Task)"
        verbose_name_plural = "할 일(Task) 목록"

    def __str__(self):
        prefix = "[AI추천] " if self.is_ai_recommended else ""
        return f"{prefix}Task-{self.id}: {self.title} ({self.status})"


class TaskComment(models.Model):
    """
    [추천사항 3] 특정 업무(Task) 내에서 직원간 혹은 AI 시스템과 소통하기 위한 댓글 피드
    """
    id = models.AutoField(primary_key=True, db_column="id", verbose_name="댓글 ID")
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        db_column="task_id", 
        related_name="comments", 
        verbose_name="소속 업무"
    )
    employee = models.ForeignKey(
        "employees.Employee", 
        on_delete=models.CASCADE, 
        db_column="employeeid", 
        verbose_name="작성자"
    )
    comment = models.TextField(db_column="comment", verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True, db_column="createdat", verbose_name="작성 일시")

    class Meta:
        db_table = "taskcomment"
        verbose_name = "업무 댓글"
        verbose_name_plural = "업무 댓글 목록"

    def __str__(self):
        return f"Comment by {self.employee.lastname} on Task-{self.task_id}"


class WorkNotification(models.Model):
    """
    [추천사항 2] Vue 3 네비게이션 바 우측 상단 종모양 아이콘에 실시간으로 보일 알림 전표 테이블
    """
    id = models.AutoField(primary_key=True, db_column="id", verbose_name="알림 ID")
    
    # 알림을 수신할 대상 직원
    employee = models.ForeignKey(
        "employees.Employee", 
        on_delete=models.CASCADE, 
        db_column="employeeid", 
        related_name="notifications",
        verbose_name="수신 직원"
    )
    
    message = models.CharField(max_length=255, db_column="message", verbose_name="알림 내용")
    is_read = models.BooleanField(default=False, db_column="is_read", verbose_name="읽음 여부")
    
    # 알림 클릭 시 프론트엔드(Vue Router)에서 해당 메뉴나 상세페이지로 다이렉트 점프할 경로
    # 예: '/procurement/orders/5' 또는 '/works/tasks/12'
    redirect_url = models.CharField(max_length=200, blank=True, null=True, db_column="redirect_url", verbose_name="이동 URL 경로")
    
    created_at = models.DateTimeField(auto_now_add=True, db_column="createdat", verbose_name="알림 발생 일시")

    class Meta:
        db_table = "worknotification"
        verbose_name = "업무 알림"
        verbose_name_plural = "업무 알림 목록"
        ordering = ['-created_at']  # 최신 알림이 가장 위로 오도록 정렬

    def __str__(self):
        status = "읽음" if self.is_read else "미읽음"
        return f"[{status}] {self.employee.lastname}님 - {self.message[:20]}"


class Memo(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="memos",
        verbose_name="작성자"
    )
    content = models.TextField(verbose_name="내용")
    is_pinned = models.BooleanField(default=False, verbose_name="고정 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memo"
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"[{self.employee.lastname}] {self.content[:30]}"