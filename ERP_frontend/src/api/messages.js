import http from './http'

export const messagesApi = {
  channels: () => http.get('messages/channels/'),
  channel: (id) => http.get(`messages/channels/${id}/`),
  channelMessages: (channelId) => http.get(`messages/channels/${channelId}/messages/`),
  sendMessage: (channelId, content) =>
    http.post(`messages/channels/${channelId}/messages/`, { content }),
  startDirect: (employeeId) =>
    http.post('messages/start-direct/', { employeeid: employeeId }),
  createChannel: (data) => http.post('messages/channels/', data),
  deleteChannel: (channelId) => http.delete(`messages/channels/${channelId}/`),
  markRead: (messageId) => http.post(`messages/messages/${messageId}/read/`),
  markChannelRead: (channelId) => http.post(`messages/channels/${channelId}/read/`),
  addMember: (channelId, employeeid) =>
    http.post(`messages/channels/${channelId}/members/`, { employeeid }),
  leaveChannel: (channelId) => http.delete(`messages/channels/${channelId}/leave/`),
  channelMessagesAfter: (channelId, afterId) =>
    http.get(`messages/channels/${channelId}/messages/${afterId ? `?after=${afterId}` : ''}`),
  employees: () => http.get('employees/'),
}

function _getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

export function createMessageSocket(channelId, handlers) {
  const token = _getCookie('erp-access')
  const wsBase = window.location.hostname === 'localhost'
    ? 'ws://localhost:8000'
    : `wss://ssafy-international-env.eba-xbft237q.ap-northeast-2.elasticbeanstalk.com`
  const url = `${wsBase}/ws/messages/${channelId}/${token ? `?token=${token}` : ''}`
  const ws = new WebSocket(url)

  ws.onopen = () => handlers.onOpen?.()
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handlers.onMessage?.(data)
    } catch {}
  }
  ws.onclose = (e) => handlers.onClose?.(e)
  ws.onerror = (e) => handlers.onError?.(e)

  return ws
}