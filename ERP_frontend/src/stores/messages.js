import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { messagesApi, createMessageSocket } from '@/api/messages'

export const useMessagesStore = defineStore('messages', () => {
  const channels = ref([])
  const activeChannel = ref(null)
  const messages = ref([])
  const employees = ref([])
  const loading = ref(false)

  // WebSocket
  const _ws = ref(null)
  const wsConnected = ref(false)

  // 전체 미읽음 수 (채널 목록 기반)
  const totalUnread = computed(() =>
    channels.value.reduce((acc, ch) => acc + (ch.unread_count || 0), 0)
  )

  // ── 채널 ─────────────────────────────────────────────────────────────

  async function fetchChannels() {
    const res = await messagesApi.channels()
    channels.value = res.data
  }

  async function fetchEmployees() {
    const res = await messagesApi.employees()
    employees.value = res.data
  }

  async function openChannel(channelId) {
    loading.value = true
    try {
      const [chRes, msgRes] = await Promise.all([
        messagesApi.channel(channelId),
        messagesApi.channelMessages(channelId),
      ])
      activeChannel.value = chRes.data
      messages.value = msgRes.data
      // 읽음 처리 (last_read_at 갱신 + unread_count 0으로 + 메시지별 read_count 즉시 반영)
      try {
        const readRes = await messagesApi.markChannelRead(channelId)
        updateReadCounts(readRes.data.read_counts)
        const ch = channels.value.find((c) => c.id === channelId)
        if (ch) ch.unread_count = 0
      } catch { /* 읽음 처리 실패해도 채팅방 진입은 유지 */ }
    } finally {
      loading.value = false
    }
  }

  // 마지막 메시지 이후 새 메시지만 fetch (폴링 fallback용)
  async function fetchNewMessages(channelId) {
    if (!activeChannel.value || activeChannel.value.id !== channelId) return
    const lastId = messages.value.at(-1)?.id
    const res = await messagesApi.channelMessagesAfter(channelId, lastId)
    res.data.forEach((msg) => pushMessage(msg))
  }

  async function startDirect(employeeId) {
    const res = await messagesApi.startDirect(employeeId)
    const channel = res.data
    if (!channels.value.find((c) => c.id === channel.id)) {
      channels.value.push(channel)
    }
    await openChannel(channel.id)
  }

  async function createChannel(data) {
    const res = await messagesApi.createChannel(data)
    channels.value.unshift(res.data)
    return res.data
  }

  async function deleteChannel(channelId) {
    await messagesApi.deleteChannel(channelId)
    channels.value = channels.value.filter((c) => c.id !== channelId)
    if (activeChannel.value?.id === channelId) {
      activeChannel.value = null
      messages.value = []
    }
  }

  async function addMember(channelId, employeeid) {
    const res = await messagesApi.addMember(channelId, employeeid)
    if (activeChannel.value?.id === channelId) {
      activeChannel.value = res.data
    }
    return res.data
  }

  async function leaveChannel(channelId) {
    await messagesApi.leaveChannel(channelId)
    channels.value = channels.value.filter((c) => c.id !== channelId)
    if (activeChannel.value?.id === channelId) {
      activeChannel.value = null
      messages.value = []
    }
  }

  // ── 메시지 ───────────────────────────────────────────────────────────

  // 항상 REST로 전송 → 즉시 로컬 반영
  // REST 뷰가 WebSocket 그룹에도 브로드캐스트하므로 다른 사원도 실시간 수신
  async function sendMessage(content) {
    if (!activeChannel.value) return
    const res = await messagesApi.sendMessage(activeChannel.value.id, content)
    // 중복 방지 후 즉시 반영
    pushMessage(res.data)
  }

  function pushMessage(msg) {
    if (!activeChannel.value) return
    if (msg.channel !== activeChannel.value.id) return
    if (messages.value.find((m) => m.id === msg.id)) return
    messages.value.push(msg)
  }

  function updateReadCounts(readCountsMap) {
    messages.value.forEach((msg) => {
      const key = String(msg.id)
      if (key in readCountsMap) msg.read_count = readCountsMap[key]
    })
  }

  function handleChannelDeleted(channelId) {
    channels.value = channels.value.filter((c) => c.id !== channelId)
    if (activeChannel.value?.id === channelId) {
      activeChannel.value = null
      messages.value = []
    }
  }

  // 채널 목록의 unread_count 증가 (WebSocket으로 새 메시지 수신 시)
  function incrementUnread(channelId) {
    const ch = channels.value.find((c) => c.id === channelId)
    if (ch) ch.unread_count = (ch.unread_count || 0) + 1
  }

  // ── WebSocket ─────────────────────────────────────────────────────────

  function connectWS(channelId, extraHandlers = {}) {
    disconnectWS()
    const ws = createMessageSocket(channelId, {
      onOpen: () => { wsConnected.value = true },
      onMessage: (data) => {
        if (data.type === 'message') {
          // REST 전송으로 이미 로컬에 있을 수 있으므로 pushMessage가 중복 방지
          pushMessage(data.message)
          extraHandlers.onMessage?.(data.message)
        } else if (data.type === 'read_update') {
          updateReadCounts(data.read_counts)
        } else if (data.type === 'channel_deleted') {
          handleChannelDeleted(data.channel_id)
          extraHandlers.onChannelDeleted?.(data.channel_id)
        }
      },
      onClose: () => { wsConnected.value = false; _ws.value = null },
      onError: () => { wsConnected.value = false },
    })
    _ws.value = ws
  }

  function disconnectWS() {
    if (_ws.value) { _ws.value.close(); _ws.value = null }
    wsConnected.value = false
  }

  return {
    channels, activeChannel, messages, employees, loading, totalUnread, wsConnected,
    fetchChannels, fetchEmployees, openChannel, fetchNewMessages,
    startDirect, createChannel, deleteChannel, addMember, leaveChannel,
    sendMessage, pushMessage, updateReadCounts, handleChannelDeleted,
    incrementUnread, connectWS, disconnectWS,
  }
})
