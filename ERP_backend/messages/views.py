"""
messages/views.py
- Channel, ChannelMember, Message, MessageRead
- 핵심 정책:
  * write_level(작성 최소 레벨)은 클라이언트를 믿지 않고 서버에서 channel_type 으로 결정
  * 공지(announcement)=4, 그 외=1
  * DM 은 별도 탭이 아니라 start_direct 로 1:1 채널을 찾거나 생성
  * 우선 REST + 폴링(?after=마지막 메시지 id), WebSocket(Channels)은 나중에
- 역할 레벨/본인 사원 조회는 employees 앱의 헬퍼를 재사용
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Channel, ChannelMember, Message, MessageRead
from .serializers import ChannelSerializer, MessageSerializer, ChannelUpdateSerializer
from employees.models import Employee
from employees.views import get_level, current_employee   # 코드 매핑 헬퍼 재사용


# channel_type → 작성 최소 레벨 (서버에서 강제 결정)
WRITE_LEVEL_BY_TYPE = {
    'announcement': 4,
    'department': 1,
    'team': 1,
    'direct': 1,
}


# =====================================================================
# Channel — 내가 속한 채널 목록 / 채널 생성
# =====================================================================
@api_view(['GET', 'POST'])
def channel_list(request):
    me = current_employee(request)

    if request.method == 'GET':
        # 내가 멤버로 들어가 있는 채널만
        my_channel_ids = ChannelMember.objects.filter(
            employee=me
        ).values_list('channel_id', flat=True)
        qs = Channel.objects.filter(id__in=my_channel_ids)
        return Response(ChannelSerializer(qs, many=True).data)

    # POST (채널 생성)
    channel_type = request.data.get('channel_type', 'team')
    if channel_type not in WRITE_LEVEL_BY_TYPE:
        return Response(
            {'detail': f'허용되지 않은 channel_type: {channel_type}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ChannelSerializer(data=request.data)
    if serializer.is_valid():
        # write_level / channel_type / created_by 는 서버가 결정해서 주입
        channel = serializer.save(
            created_by=me,
            channel_type=channel_type,
            write_level=WRITE_LEVEL_BY_TYPE[channel_type],
        )
        # 생성자는 자동으로 멤버 등록
        ChannelMember.objects.create(channel=channel, employee=me)
        return Response(ChannelSerializer(channel).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)

    if request.method == 'GET':
        return Response(ChannelSerializer(channel).data)

    if request.method == 'PUT':
        # 이름/설명 정도만 수정. write_level/type 은 서버 정책이라 그대로 둠
        serializer = ChannelUpdateSerializer(channel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ChannelSerializer(channel).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    channel.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# =====================================================================
# Message — 채널 메시지 조회(폴링) / 작성(write_level 검사)
# =====================================================================
@api_view(['GET', 'POST'])
def channel_messages(request, channel_id):
    channel = get_object_or_404(Channel, pk=channel_id)
    me = current_employee(request)

    # 멤버가 아니면 읽기/쓰기 모두 차단
    is_member = ChannelMember.objects.filter(channel=channel, employee=me).exists()
    if not is_member:
        return Response(
            {'detail': '이 채널의 멤버가 아닙니다.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'GET':
        qs = Message.objects.filter(channel=channel).order_by('created_at')
        # 폴링: 마지막으로 받은 메시지 id 이후 것만
        after = request.query_params.get('after')
        if after:
            qs = qs.filter(id__gt=after)
        return Response(MessageSerializer(qs, many=True).data)

    # POST (메시지 작성) → write_level 검사
    if get_level(me) < channel.write_level:
        return Response(
            {'detail': f'이 채널은 레벨 {channel.write_level} 이상만 작성할 수 있습니다.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        # channel / author 는 서버가 주입 (클라이언트가 못 바꾸게)
        serializer.save(channel=channel, author=me)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================
# start_direct — 상대와의 1:1 DM 채널 찾기 or 생성
# =====================================================================
@api_view(['POST'])
def start_direct(request):
    me = current_employee(request)
    target_id = request.data.get('employeeid')
    if not target_id:
        return Response(
            {'detail': 'employeeid 가 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    target = get_object_or_404(Employee, pk=target_id)

    if target == me:
        return Response(
            {'detail': '자기 자신과는 DM을 시작할 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 1) 이미 둘 사이에 direct 채널이 있는지 확인
    #    내가 속한 direct 채널 중 상대도 멤버인 것
    my_direct_ids = ChannelMember.objects.filter(
        employee=me, channel__channel_type='direct'
    ).values_list('channel_id', flat=True)
    existing = Channel.objects.filter(
        id__in=my_direct_ids,
        channelmember__employee=target,   # ChannelMember 역참조
    ).first()
    if existing:
        return Response(ChannelSerializer(existing).data)

    # 2) 없으면 새 direct 채널 생성 + 두 명 멤버 등록
    channel = Channel.objects.create(
        name=f'DM:{me.employeeid}-{target.employeeid}',
        channel_type='direct',
        write_level=WRITE_LEVEL_BY_TYPE['direct'],
        created_by=me,
    )
    ChannelMember.objects.create(channel=channel, employee=me)
    ChannelMember.objects.create(channel=channel, employee=target)
    return Response(ChannelSerializer(channel).data, status=status.HTTP_201_CREATED)


# =====================================================================
# read — 메시지 읽음 처리 (MessageRead through 테이블)
# =====================================================================
@api_view(['POST'])
def mark_read(request, message_id):
    me = current_employee(request)
    message = get_object_or_404(Message, pk=message_id)

    # 중복 방지: 이미 있으면 그대로
    MessageRead.objects.get_or_create(message=message, employee=me)
    return Response({'detail': '읽음 처리되었습니다.'}, status=status.HTTP_200_OK)