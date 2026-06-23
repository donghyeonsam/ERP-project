# messages/serializers.py
from rest_framework import serializers
from .models import Channel, ChannelMember, Message, MessageRead


class ChannelSerializer(serializers.ModelSerializer):

    member_count  = serializers.IntegerField(source="members.count", read_only=True)
    unread_count  = serializers.SerializerMethodField()
    dm_partner_name = serializers.SerializerMethodField()
    creator_id    = serializers.SerializerMethodField()

    class Meta:
        model  = Channel
        fields = "__all__"

    def get_creator_id(self, obj):
        return obj.created_by.employeeid if obj.created_by else None

    def get_dm_partner_name(self, obj):
        if obj.channel_type != 'direct':
            return None
        request = self.context.get('request')
        if not request:
            return None
        me = getattr(request.user, 'employee', None)
        if not me:
            return None
        partner = obj.members.exclude(employee=me).select_related('employee').first()
        if partner:
            return f"{partner.employee.lastname}{partner.employee.firstname}"
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        me = getattr(request.user, 'employee', None)
        if not me:
            return 0
        try:
            member = obj.members.get(employee=me)
            if member.last_read_at:
                return obj.messages.filter(created_at__gt=member.last_read_at).count()
            return obj.messages.count()
        except ChannelMember.DoesNotExist:
            return 0


class ChannelMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ChannelMember
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):

    sender_name = serializers.SerializerMethodField()
    read_count  = serializers.IntegerField(source="reads.count", read_only=True)

    class Meta:
        model  = Message
        fields = "__all__"
        # channel, sender 는 뷰에서 save(channel=..., sender=...) 로 주입
        # created_at, read_by 는 자동 관리 필드
        read_only_fields = ['channel', 'sender', 'created_at', 'edited_at', 'read_by']

    def get_sender_name(self, obj):
        if obj.sender:
            return f"{obj.sender.lastname}{obj.sender.firstname}"
        return None


class MessageReadSerializer(serializers.ModelSerializer):

    employee_name = serializers.SerializerMethodField()

    class Meta:
        model  = MessageRead
        fields = "__all__"

    def get_employee_name(self, obj):
        return f"{obj.employee.lastname}{obj.employee.firstname}"


class ChannelUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Channel
        fields = ('name',)
