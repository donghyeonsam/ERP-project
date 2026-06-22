from django.db import models
from employees.models import Employee

# Create your models here.
class Channel(models.Model):

    CHANNEL_TYPE = [
        ("announcement", "전체 공지"),
        ("department", "부서 채널"),
        ("team", "팀 채널"),
        ("direct", "개인 DM"),
    ]

    name = models.CharField(max_length=80, blank=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE,
                                    default="direct")
    department = models.CharField(max_length=60, blank=True, null=True)  
    team = models.CharField(max_length=60, blank=True, null=True)  
    write_level = models.PositiveSmallIntegerField(default=1)  
    created_by = models.ForeignKey("employees.Employee", on_delete=models.SET_NULL,
                                     null=True, related_name="created_channels")
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = "channel"
 
    def __str__(self):
        return f"[{self.channel_type}] {self.name or 'DM'}"
    

class ChannelMember(models.Model):

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="members")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="channels")
    last_read_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "channelmember"
        unique_together = ("channel", "employee")


class Message(models.Model):

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="sent_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    read_by = models.ManyToManyField(Employee, through="MessageRead", related_name="read_messages")

    class Meta:
        db_table = "message"
        ordering = ["created_at"]


class MessageRead(models.Model):

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reads")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="message_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messageread"
        unique_together = ("message", "employee")
