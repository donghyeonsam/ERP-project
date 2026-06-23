"""
messages/consumers.py
WebSocket consumer for real-time chat.
- Group name: chat_<channel_id>
- Events received from client: {type: 'message', content: '...'}
- Events sent to client:
    {type: 'message', message: {...}}        - new message
    {type: 'read_update', read_counts: {...}} - read receipt update
    {type: 'channel_deleted', channel_id: n} - channel was deleted
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework.renderers import JSONRenderer

from .models import Channel, ChannelMember, Message, MessageRead
from .serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.channel_id = int(self.scope['url_route']['kwargs']['channel_id'])
        self.room_group_name = f'chat_{self.channel_id}'

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.employee = await self._get_employee(user)
        if self.employee is None:
            await self.close(code=4001)
            return

        if not await self._is_member():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return

        if data.get('type') == 'message':
            content = (data.get('content') or '').strip()
            if not content:
                return
            if not await self._can_write():
                return

            msg_data = await self._save_and_serialize(content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'chat_message', 'message': msg_data},
            )

    # ── group event handlers ───────────────────────────────────────────

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(
            {'type': 'message', 'message': event['message']}
        ))

    async def chat_read_update(self, event):
        await self.send(text_data=json.dumps(
            {'type': 'read_update', 'read_counts': event['read_counts']}
        ))

    async def chat_channel_deleted(self, event):
        await self.send(text_data=json.dumps(
            {'type': 'channel_deleted', 'channel_id': event['channel_id']}
        ))

    # ── DB helpers (run in thread pool) ───────────────────────────────

    @database_sync_to_async
    def _get_employee(self, user):
        return getattr(user, 'employee', None)

    @database_sync_to_async
    def _is_member(self):
        return ChannelMember.objects.filter(
            channel_id=self.channel_id, employee=self.employee
        ).exists()

    @database_sync_to_async
    def _can_write(self):
        try:
            channel = Channel.objects.get(pk=self.channel_id)
            # 공지 채널만 레벨 체크, 나머지는 멤버이면 누구나 작성 가능
            if channel.channel_type != 'announcement':
                return True
            from employees.views import get_level
            return get_level(self.employee) >= channel.write_level
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def _save_and_serialize(self, content):
        msg = Message.objects.create(
            channel_id=self.channel_id,
            sender=self.employee,
            content=content,
        )
        # Mark sender as having read
        MessageRead.objects.get_or_create(message=msg, employee=self.employee)
        # Re-fetch with related data for serialization
        msg = Message.objects.select_related('sender').get(pk=msg.pk)
        rendered = JSONRenderer().render(MessageSerializer(msg).data)
        return json.loads(rendered)
