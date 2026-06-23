# messages/serializers.py
from rest_framework import serializers
from .models import Channel, ChannelMember, Message, MessageRead


class ChannelSerializer(serializers.ModelSerializer):

    member_count = serializers.IntegerField(source="members.count", read_only=True)
    
    class Meta:
        model  = Channel
        fields = "__all__"


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
        model = Channel
        fields = ('name', 'description') 