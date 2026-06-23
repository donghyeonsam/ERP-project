"""
messages/views.py
- Channel, ChannelMember, Message, MessageRead
- channel_type 별 write_level 은 서버에서 강제 결정
- WebSocket broadcast 는 InMemoryChannelLayer 통해 처리
"""
import json
from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Channel, ChannelMember, Message, MessageRead
from .serializers import ChannelSerializer, MessageSerializer, ChannelUpdateSerializer
from employees.models import Employee
from employees.views import get_level, current_employee


WRITE_LEVEL_BY_TYPE = {
    'announcement': 4,
    'department': 1,
    'team': 1,
    'direct': 1,
}


def _ws_group_send(group_name, payload):
    """WebSocket channel layer group send (동기 컨텍스트에서 호출)"""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        layer = get_channel_layer()
        if layer:
            async_to_sync(layer.group_send)(group_name, payload)
    except Exception:
        pass


# =====================================================================
# Channel — 내가 속한 채널 목록 / 채널 생성
# =====================================================================
@api_view(['GET', 'POST'])
def channel_list(request):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    if request.method == 'GET':
        my_channel_ids = ChannelMember.objects.filter(
            employee=me
        ).values_list('channel_id', flat=True)
        qs = Channel.objects.filter(id__in=my_channel_ids)
        return Response(ChannelSerializer(qs, many=True, context={'request': request}).data)

    # POST — 채널 생성
    channel_type = request.data.get('channel_type', 'team')
    if channel_type not in WRITE_LEVEL_BY_TYPE:
        return Response(
            {'detail': f'허용되지 않은 channel_type: {channel_type}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ChannelSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        channel = serializer.save(
            created_by=me,
            channel_type=channel_type,
            write_level=WRITE_LEVEL_BY_TYPE[channel_type],
        )
        # 생성자 자동 멤버 등록
        ChannelMember.objects.create(channel=channel, employee=me)

        # 공지 채널 → 전 직원 자동 추가
        if channel_type == 'announcement':
            all_others = Employee.objects.exclude(pk=me.pk)
            ChannelMember.objects.bulk_create(
                [ChannelMember(channel=channel, employee=emp) for emp in all_others],
                ignore_conflicts=True,
            )
        else:
            # 지정 멤버 추가
            member_ids = request.data.get('member_ids', [])
            for emp_id in member_ids:
                try:
                    emp = Employee.objects.get(pk=emp_id)
                    if emp != me:
                        ChannelMember.objects.get_or_create(channel=channel, employee=emp)
                except Employee.DoesNotExist:
                    pass

        return Response(
            ChannelSerializer(channel, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    if request.method == 'GET':
        return Response(ChannelSerializer(channel, context={'request': request}).data)

    if request.method == 'PUT':
        serializer = ChannelUpdateSerializer(channel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ChannelSerializer(channel, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE — 생성자만 허용
    if channel.created_by != me:
        return Response({'detail': '채널 생성자만 삭제할 수 있습니다.'}, status=403)

    # 삭제 전 WebSocket 알림 (연결된 클라이언트가 UI 닫을 수 있도록)
    _ws_group_send(
        f'chat_{channel_id}',
        {'type': 'chat_channel_deleted', 'channel_id': channel_id},
    )
    channel.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Message — 채널 메시지 조회(폴링) / 작성
# =====================================================================
@api_view(['GET', 'POST'])
def channel_messages(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    is_member = ChannelMember.objects.filter(channel=channel, employee=me).exists()
    if not is_member:
        return Response({'detail': '이 채널의 멤버가 아닙니다.'}, status=403)

    if request.method == 'GET':
        qs = Message.objects.filter(channel=channel).order_by('created_at')
        after = request.query_params.get('after')
        if after:
            qs = qs.filter(id__gt=after)
        return Response(MessageSerializer(qs, many=True).data)

    # POST — 공지 채널은 레벨 체크, 그 외는 멤버면 누구나 작성 가능
    if channel.channel_type == 'announcement' and get_level(me) < channel.write_level:
        return Response(
            {'detail': f'이 채널은 레벨 {channel.write_level} 이상만 작성할 수 있습니다.'},
            status=403,
        )

    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        msg = serializer.save(channel=channel, sender=me)
        # 발신자 읽음 처리
        MessageRead.objects.get_or_create(message=msg, employee=me)
        # 직렬화 (sender 관계 로드)
        msg = Message.objects.select_related('sender').get(pk=msg.pk)
        msg_data = json.loads(JSONRenderer().render(MessageSerializer(msg).data))
        # WebSocket 그룹에 브로드캐스트 — 다른 사원이 실시간으로 수신
        _ws_group_send(
            f'chat_{channel_id}',
            {'type': 'chat_message', 'message': msg_data},
        )
        return Response(msg_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================
# start_direct
# =====================================================================
@api_view(['POST'])
def start_direct(request):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    target_id = request.data.get('employeeid')
    if not target_id:
        return Response({'detail': 'employeeid 가 필요합니다.'}, status=400)
    target = get_object_or_404(Employee, pk=target_id)

    if target == me:
        return Response({'detail': '자기 자신과는 DM을 시작할 수 없습니다.'}, status=400)

    my_direct_ids = ChannelMember.objects.filter(
        employee=me, channel__channel_type='direct'
    ).values_list('channel_id', flat=True)
    existing = Channel.objects.filter(
        id__in=my_direct_ids,
        members__employee=target,
    ).first()
    if existing:
        return Response(ChannelSerializer(existing, context={'request': request}).data)

    channel = Channel.objects.create(
        name=f'DM:{me.employeeid}-{target.employeeid}',
        channel_type='direct',
        write_level=WRITE_LEVEL_BY_TYPE['direct'],
        created_by=me,
    )
    ChannelMember.objects.create(channel=channel, employee=me)
    ChannelMember.objects.create(channel=channel, employee=target)
    return Response(
        ChannelSerializer(channel, context={'request': request}).data,
        status=status.HTTP_201_CREATED,
    )


# =====================================================================
# add_channel_member — 채널에 멤버 추가
# =====================================================================
@api_view(['POST'])
def add_channel_member(request, channel_id):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    channel = get_object_or_404(Channel, pk=channel_id)
    if not ChannelMember.objects.filter(channel=channel, employee=me).exists():
        return Response({'detail': '채널 멤버가 아닙니다.'}, status=403)

    emp_id = request.data.get('employeeid')
    if not emp_id:
        return Response({'detail': 'employeeid 가 필요합니다.'}, status=400)

    emp = get_object_or_404(Employee, pk=emp_id)
    _, created = ChannelMember.objects.get_or_create(channel=channel, employee=emp)
    if not created:
        return Response({'detail': '이미 멤버입니다.'}, status=400)

    return Response(ChannelSerializer(channel, context={'request': request}).data)


# =====================================================================
# leave_channel — 채널에서 나가기
# =====================================================================
@api_view(['DELETE'])
def leave_channel(request, channel_id):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    channel = get_object_or_404(Channel, pk=channel_id)
    deleted, _ = ChannelMember.objects.filter(channel=channel, employee=me).delete()
    if deleted == 0:
        return Response({'detail': '채널 멤버가 아닙니다.'}, status=400)

    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# mark_read — 단일 메시지
# =====================================================================
@api_view(['POST'])
def mark_read(request, message_id):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    message = get_object_or_404(Message, pk=message_id)
    MessageRead.objects.get_or_create(message=message, employee=me)
    return Response({'detail': '읽음 처리되었습니다.'})


# =====================================================================
# mark_channel_read — 채널 내 전체 메시지 읽음 처리 + WebSocket 브로드캐스트
# =====================================================================
@api_view(['POST'])
def mark_channel_read(request, channel_id):
    me = current_employee(request)
    if me is None:
        return Response({'detail': '사원 정보를 찾을 수 없습니다.'}, status=403)

    channel = get_object_or_404(Channel, pk=channel_id)
    if not ChannelMember.objects.filter(channel=channel, employee=me).exists():
        return Response({'detail': '채널 멤버가 아닙니다.'}, status=403)

    # last_read_at 업데이트 (unread_count 계산 기준)
    ChannelMember.objects.filter(channel=channel, employee=me).update(
        last_read_at=datetime.now()
    )

    messages = list(Message.objects.filter(channel=channel))
    for msg in messages:
        MessageRead.objects.get_or_create(message=msg, employee=me)

    # 최신 read_count 집계
    read_counts = {str(msg.pk): msg.reads.count() for msg in messages}

    # WebSocket 으로 read_update 브로드캐스트
    _ws_group_send(
        f'chat_{channel_id}',
        {'type': 'chat_read_update', 'read_counts': read_counts},
    )

    return Response({'detail': 'ok', 'read_counts': read_counts})
