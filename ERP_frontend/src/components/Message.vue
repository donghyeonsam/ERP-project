<template>
  <!-- FAB -->
  <button class="messenger-fab" :class="{ open: isOpen }" @click="toggleMessenger" title="메신저">
    <i :class="['bi', isOpen ? 'bi-x-lg' : 'bi-chat-dots-fill']"></i>
    <span v-if="store.totalUnread > 0" class="fab-badge">
      {{ store.totalUnread > 99 ? '99+' : store.totalUnread }}
    </span>
  </button>

  <!-- Chat window -->
  <div v-if="isOpen" class="messenger-window shadow-lg">

    <!-- Header -->
    <div class="messenger-header">
      <div class="d-flex gap-1">
        <button :class="['tab-btn', tab === 'channels' ? 'active' : '']"
          @click="tab = 'channels'; view = 'list'; creating = false">
          <i class="bi bi-chat-left-text-fill me-1" style="font-size:0.7rem"></i>채널
        </button>
        <button :class="['tab-btn', tab === 'employees' ? 'active' : '']" @click="switchToEmployees">
          <i class="bi bi-people-fill me-1" style="font-size:0.7rem"></i>직원
        </button>
      </div>
      <span class="fw-semibold small">메신저</span>
    </div>

    <!-- ══ 채널 탭 ══════════════════════════════════════════════════ -->
    <template v-if="tab === 'channels' && view === 'list'">
      <!-- 채널 생성 폼 -->
      <div v-if="creating" class="create-form">
        <div class="fw-semibold small mb-2">새 채팅방 만들기</div>
        <input v-model="newCh.name" class="form-control form-control-sm mb-2" placeholder="채팅방 이름" />
        <select v-model="newCh.channel_type" class="form-select form-select-sm mb-2">
          <option value="team">팀 채널</option>
          <option value="department">부서 채널</option>
          <option v-if="userLevel >= 4" value="announcement">전체 공지 채널</option>
        </select>
        <div v-if="newCh.channel_type === 'department'" class="mb-2">
          <input v-model="newCh.department" class="form-control form-control-sm" placeholder="부서명" />
        </div>
        <div v-if="newCh.channel_type === 'team'" class="mb-2">
          <input v-model="newCh.team" class="form-control form-control-sm" placeholder="팀명" />
        </div>
        <!-- 멤버 초대 -->
        <div v-if="newCh.channel_type !== 'announcement'" class="mb-2">
          <div class="d-flex gap-1 flex-wrap mb-1">
            <span v-for="m in newCh.members" :key="m.employeeid"
              class="badge bg-primary d-flex align-items-center gap-1" style="font-size:0.7rem">
              {{ m.lastname }}{{ m.firstname }}
              <i class="bi bi-x" style="cursor:pointer" @click="removeMember(m)"></i>
            </span>
          </div>
          <div class="position-relative">
            <input v-model="memberSearch" class="form-control form-control-sm"
              placeholder="멤버 검색 후 클릭으로 추가..."
              @focus="showMemberDrop = true" @blur="hideMemberDrop" />
            <div v-if="showMemberDrop && filteredMemberCandidates.length" class="member-drop shadow-sm">
              <div v-for="emp in filteredMemberCandidates" :key="emp.employeeid"
                class="member-drop-item" @mousedown.prevent="addMemberToForm(emp)">
                <div class="emp-avatar-sm">{{ (emp.lastname || '?').charAt(0) }}</div>
                <span class="small">{{ emp.lastname }}{{ emp.firstname }} ({{ emp.title || '직원' }})</span>
              </div>
            </div>
          </div>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-primary flex-grow-1" @click="doCreateChannel" :disabled="creatingLoading">
            <span v-if="creatingLoading" class="spinner-border spinner-border-sm me-1"></span>만들기
          </button>
          <button class="btn btn-sm btn-outline-secondary" @click="creating = false">취소</button>
        </div>
      </div>

      <!-- 채널 목록 -->
      <div class="messenger-body">
        <div v-if="loadingChannels" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
        <template v-else>
          <div v-if="announcementChannels.length" class="ch-group-label"><i class="bi bi-megaphone me-1"></i>전체 공지</div>
          <div v-for="ch in announcementChannels" :key="ch.id" class="channel-item announcement-ch" @click="openChannel(ch)">
            <div class="channel-icon announcement-icon"><i class="bi bi-megaphone-fill"></i></div>
            <div class="flex-grow-1 overflow-hidden">
              <div class="small fw-semibold text-truncate">{{ ch.name }}</div>
              <div class="text-muted text-truncate" style="font-size:0.7rem">전체 공지 채널</div>
            </div>
            <span v-if="ch.unread_count > 0" class="ch-unread-badge">{{ ch.unread_count > 99 ? '99+' : ch.unread_count }}</span>
          </div>

          <div v-if="groupChannels.length" class="ch-group-label"><i class="bi bi-people me-1"></i>그룹 채널</div>
          <div v-for="ch in groupChannels" :key="ch.id" class="channel-item" @click="openChannel(ch)">
            <div class="channel-icon">
              <i class="bi" :class="ch.channel_type === 'department' ? 'bi-building' : 'bi-people'"></i>
            </div>
            <div class="flex-grow-1 overflow-hidden">
              <div class="small fw-semibold text-truncate">{{ ch.name }}</div>
              <div class="text-muted text-truncate" style="font-size:0.7rem">
                {{ ch.channel_type === 'department' ? '부서' : '팀' }} · {{ ch.member_count }}명
              </div>
            </div>
            <span v-if="ch.unread_count > 0" class="ch-unread-badge">{{ ch.unread_count > 99 ? '99+' : ch.unread_count }}</span>
          </div>

          <div v-if="dmChannels.length" class="ch-group-label"><i class="bi bi-person me-1"></i>다이렉트 메시지</div>
          <div v-for="ch in dmChannels" :key="ch.id" class="channel-item" @click="openChannel(ch)">
            <div class="channel-icon dm-icon"><i class="bi bi-person-fill"></i></div>
            <div class="flex-grow-1 overflow-hidden">
              <div class="small fw-semibold text-truncate">{{ ch.dm_partner_name || 'DM' }}</div>
              <div class="text-muted text-truncate" style="font-size:0.7rem">개인 메시지</div>
            </div>
            <span v-if="ch.unread_count > 0" class="ch-unread-badge">{{ ch.unread_count > 99 ? '99+' : ch.unread_count }}</span>
          </div>

          <div v-if="store.channels.length === 0" class="text-muted small text-center py-5">
            <i class="bi bi-chat-left-text fs-3 d-block mb-2"></i>채널이 없습니다
          </div>
        </template>
      </div>

      <div class="create-channel-btn" @click="creating = !creating">
        <i class="bi bi-plus-circle me-1"></i><span class="small">새 채팅방 만들기</span>
      </div>
    </template>

    <!-- ══ 직원 탭 ══════════════════════════════════════════════════ -->
    <template v-if="tab === 'employees' && view === 'list'">
      <div class="p-2 border-bottom">
        <input v-model="empSearch" type="text" class="form-control form-control-sm" placeholder="직원 검색..." />
      </div>
      <div class="messenger-body">
        <div v-if="loadingEmployees" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
        <div v-for="emp in filteredEmployees" :key="emp.employeeid" class="employee-item" @click="showProfile(emp)">
          <div class="emp-avatar">{{ (emp.lastname || '?').charAt(0) }}</div>
          <div class="flex-grow-1 overflow-hidden">
            <div class="small fw-semibold">{{ emp.lastname }}{{ emp.firstname }}</div>
            <div class="text-muted text-truncate" style="font-size:0.7rem">{{ emp.title || '직원' }}</div>
          </div>
          <i class="bi bi-chevron-right text-muted" style="font-size:0.75rem"></i>
        </div>
        <div v-if="filteredEmployees.length === 0 && !loadingEmployees" class="text-muted small text-center py-4">직원이 없습니다</div>
      </div>
    </template>

    <!-- ══ 직원 프로필 뷰 ══════════════════════════════════════════ -->
    <template v-if="view === 'profile' && selectedEmp">
      <div class="profile-header">
        <button class="btn btn-sm btn-link p-0 text-white me-2" @click="view = 'list'">
          <i class="bi bi-arrow-left"></i>
        </button>
        <span class="small fw-semibold text-white">직원 프로필</span>
      </div>
      <div class="profile-body">
        <div class="profile-avatar">{{ (selectedEmp.lastname || '?').charAt(0) }}</div>
        <div class="fw-bold mt-2" style="font-size:1rem">{{ selectedEmp.lastname }}{{ selectedEmp.firstname }}</div>
        <div class="text-muted small mt-1">{{ selectedEmp.title || '직원' }}</div>
        <div v-if="selectedEmp.city" class="text-muted" style="font-size:0.78rem">
          <i class="bi bi-geo-alt me-1"></i>{{ selectedEmp.city }}
        </div>
        <div v-if="selectedEmp.homephone" class="text-muted" style="font-size:0.78rem">
          <i class="bi bi-telephone me-1"></i>{{ selectedEmp.homephone }}
        </div>
        <div class="mt-3 d-flex gap-2">
          <button class="btn btn-primary btn-sm flex-grow-1"
            :disabled="selectedEmp.employeeid === currentEmployeeId"
            @click="startDMFromProfile">
            <i class="bi bi-chat-dots me-1"></i>
            {{ selectedEmp.employeeid === currentEmployeeId ? '본인' : 'DM 보내기' }}
          </button>
        </div>
      </div>
    </template>

    <!-- ══ 채팅 뷰 ══════════════════════════════════════════════════ -->
    <div v-if="view === 'chat'" class="d-flex flex-column" style="height:100%">
      <div class="messenger-chat-header">
        <button class="btn btn-sm btn-link p-0 text-dark me-2" @click="leaveChat">
          <i class="bi bi-arrow-left"></i>
        </button>
        <div class="channel-icon-sm me-2">
          <i class="bi" :class="chatChannelIcon"></i>
        </div>
        <div class="flex-grow-1 overflow-hidden">
          <div class="small fw-semibold text-truncate">{{ channelDisplayName }}</div>
          <div class="text-muted" style="font-size:0.63rem">
            멤버 {{ store.activeChannel?.member_count || '' }}명
            <span v-if="store.wsConnected" class="text-success ms-1">● 실시간</span>
          </div>
        </div>
        <!-- 멤버 추가 (그룹 채널만) -->
        <button v-if="store.activeChannel?.channel_type !== 'direct'"
          class="btn btn-sm btn-link p-0 text-primary ms-1" title="멤버 추가"
          @click="addMemberOpen = !addMemberOpen">
          <i class="bi bi-person-plus"></i>
        </button>
        <!-- 채널 삭제 (생성자만) -->
        <button v-if="isChannelCreator && store.activeChannel?.channel_type !== 'announcement'"
          class="btn btn-sm btn-link p-0 text-danger ms-1" title="채널 삭제"
          @click="confirmDeleteChannel">
          <i class="bi bi-trash3"></i>
        </button>
        <!-- 채널 나가기 -->
        <button class="btn btn-sm btn-link p-0 text-secondary ms-1" title="채널 나가기"
          @click="confirmLeaveChannel">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>

      <!-- 멤버 추가 패널 -->
      <div v-if="addMemberOpen" class="add-member-panel">
        <div class="d-flex align-items-center gap-2">
          <div class="position-relative flex-grow-1">
            <input v-model="addMemberSearch" class="form-control form-control-sm"
              placeholder="추가할 직원 검색..."
              @focus="showAddMemberDrop = true" @blur="hideAddMemberDrop" />
            <div v-if="showAddMemberDrop && addMemberCandidates.length" class="member-drop shadow-sm">
              <div v-for="emp in addMemberCandidates" :key="emp.employeeid"
                class="member-drop-item" @mousedown.prevent="doAddMember(emp)">
                <div class="emp-avatar-sm">{{ (emp.lastname || '?').charAt(0) }}</div>
                <span class="small">{{ emp.lastname }}{{ emp.firstname }}</span>
              </div>
            </div>
          </div>
          <button class="btn btn-sm btn-outline-secondary" @click="addMemberOpen = false">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>

      <div v-if="isAnnouncementChannel && !canSendMessage" class="alert alert-warning py-1 px-2 m-2 mb-0 small">
        <i class="bi bi-lock me-1"></i>레벨 4 이상만 메시지를 보낼 수 있습니다.
      </div>

      <div ref="msgContainer" class="messages-area flex-grow-1">
        <div v-if="store.loading" class="text-center py-3"><span class="spinner-border spinner-border-sm"></span></div>
        <div v-for="msg in store.messages" :key="msg.id"
          class="msg-bubble" :class="{ mine: msg.sender === currentEmployeeId }">
          <div v-if="msg.sender !== currentEmployeeId" class="msg-sender-name">{{ msg.sender_name }}</div>
          <div class="msg-row">
            <span v-if="msg.sender === currentEmployeeId && unreadNum(msg) > 0" class="unread-badge">{{ unreadNum(msg) }}</span>
            <div class="msg-content">{{ msg.content }}</div>
            <span v-if="msg.sender !== currentEmployeeId && unreadNum(msg) > 0" class="unread-badge">{{ unreadNum(msg) }}</span>
          </div>
          <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
        </div>
        <div v-if="store.messages.length === 0 && !store.loading" class="text-muted small text-center py-4">
          <i class="bi bi-chat-left fs-3 d-block mb-2"></i>첫 메시지를 보내보세요
        </div>
      </div>

      <div class="messenger-input">
        <input v-model="newMessage" type="text" class="form-control form-control-sm"
          :placeholder="canSendMessage ? '메시지 입력...' : '메시지를 보낼 권한이 없습니다'"
          :disabled="!canSendMessage"
          @keyup.enter="sendMessage" />
        <button class="btn btn-sm btn-primary ms-1" @click="sendMessage" :disabled="!canSendMessage">
          <i class="bi bi-send-fill"></i>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessagesStore } from '@/stores/messages'

const authStore = useAuthStore()
const store = useMessagesStore()

const isOpen = ref(false)
const view = ref('list')      // 'list' | 'chat' | 'profile'
const tab = ref('channels')
const newMessage = ref('')
const msgContainer = ref(null)
const loadingChannels = ref(false)
const loadingEmployees = ref(false)
const empSearch = ref('')
const selectedEmp = ref(null)

// 채널 생성 폼
const creating = ref(false)
const creatingLoading = ref(false)
const newCh = ref({ name: '', channel_type: 'team', department: '', team: '', members: [] })
const memberSearch = ref('')
const showMemberDrop = ref(false)

// 멤버 추가 패널 (채팅 중)
const addMemberOpen = ref(false)
const addMemberSearch = ref('')
const showAddMemberDrop = ref(false)

// 폴링 fallback (메시지)
let pollTimer = null
// 채널 목록 자동 갱신 (미읽음 배지 업데이트)
let channelRefreshTimer = null

const currentEmployeeId = computed(() => authStore.user?.employeeid)
const userLevel = computed(() => authStore.user?.level || 0)

const announcementChannels = computed(() => store.channels.filter((c) => c.channel_type === 'announcement'))
const groupChannels = computed(() => store.channels.filter((c) => c.channel_type === 'team' || c.channel_type === 'department'))
const dmChannels = computed(() => store.channels.filter((c) => c.channel_type === 'direct'))

const filteredEmployees = computed(() => {
  if (!empSearch.value) return store.employees
  const q = empSearch.value.toLowerCase()
  return store.employees.filter((e) =>
    `${e.lastname}${e.firstname}`.toLowerCase().includes(q) || (e.title || '').toLowerCase().includes(q)
  )
})

// 채널 생성 폼용 멤버 후보
const filteredMemberCandidates = computed(() => {
  const addedIds = new Set([currentEmployeeId.value, ...newCh.value.members.map((m) => m.employeeid)])
  const q = memberSearch.value.toLowerCase()
  return store.employees
    .filter((e) => !addedIds.has(e.employeeid))
    .filter((e) => !q || `${e.lastname}${e.firstname}`.toLowerCase().includes(q))
    .slice(0, 6)
})

// 채팅 중 멤버 추가 후보 (이미 멤버인 사람 제외는 어렵기 때문에 검색만)
const addMemberCandidates = computed(() => {
  const q = addMemberSearch.value.toLowerCase()
  if (!q) return []
  return store.employees
    .filter((e) => e.employeeid !== currentEmployeeId.value)
    .filter((e) => `${e.lastname}${e.firstname}`.toLowerCase().includes(q) || (e.title || '').toLowerCase().includes(q))
    .slice(0, 6)
})

const isAnnouncementChannel = computed(() => store.activeChannel?.channel_type === 'announcement')
const canSendMessage = computed(() => {
  if (!store.activeChannel) return true
  return isAnnouncementChannel.value ? userLevel.value >= 4 : true
})
const isChannelCreator = computed(() => {
  if (!store.activeChannel) return false
  return store.activeChannel.creator_id === currentEmployeeId.value
})
const chatChannelIcon = computed(() => {
  const t = store.activeChannel?.channel_type
  return { announcement: 'bi-megaphone-fill', department: 'bi-building', team: 'bi-people-fill', direct: 'bi-person-fill' }[t] || 'bi-chat'
})
const channelDisplayName = computed(() => {
  if (!store.activeChannel) return ''
  if (store.activeChannel.channel_type === 'direct') return store.activeChannel.dm_partner_name || 'DM'
  return store.activeChannel.name
})

function unreadNum(msg) {
  const total = store.activeChannel?.member_count || 0
  return Math.max(0, total - (msg.read_count || 0))
}

// ── 메신저 열기/닫기 ────────────────────────────────────────────────
function toggleMessenger() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadChannels()
  } else {
    clearInterval(channelRefreshTimer)
    channelRefreshTimer = null
  }
}

async function loadChannels() {
  loadingChannels.value = true
  try { await store.fetchChannels() } finally { loadingChannels.value = false }
  // 10초마다 채널 목록 갱신 (미읽음 배지 업데이트)
  clearInterval(channelRefreshTimer)
  channelRefreshTimer = setInterval(() => {
    store.fetchChannels().catch(() => {})
  }, 10000)
}

async function switchToEmployees() {
  tab.value = 'employees'
  view.value = 'list'
  if (store.employees.length === 0) {
    loadingEmployees.value = true
    try { await store.fetchEmployees() } finally { loadingEmployees.value = false }
  }
}

// ── 채널 열기 ────────────────────────────────────────────────────────
async function openChannel(ch) {
  view.value = 'chat'
  addMemberOpen.value = false
  await store.openChannel(ch.id)
  scrollToBottom()
  // WebSocket 연결
  store.connectWS(ch.id, {
    onMessage: () => scrollToBottom(),
    onChannelDeleted: () => { view.value = 'list'; tab.value = 'channels' },
  })
  // 폴링 fallback — WebSocket 연결 여부와 무관하게 3초마다 새 메시지 확인
  startPolling(ch.id)
}

function leaveChat() {
  stopPolling()
  store.disconnectWS()
  view.value = 'list'
  addMemberOpen.value = false
}

function startPolling(channelId) {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (view.value !== 'chat' || !store.activeChannel) return
    try { await store.fetchNewMessages(channelId) } catch {}
  }, 3000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

// ── 직원 → 프로필 → DM ──────────────────────────────────────────────
function showProfile(emp) {
  selectedEmp.value = emp
  view.value = 'profile'
  tab.value = 'employees'
}

async function startDMFromProfile() {
  if (!selectedEmp.value) return
  await store.startDirect(selectedEmp.value.employeeid)
  view.value = 'chat'
  tab.value = 'channels'
  addMemberOpen.value = false
  scrollToBottom()
  const chId = store.activeChannel?.id
  if (chId) {
    store.connectWS(chId, {
      onMessage: () => scrollToBottom(),
      onChannelDeleted: () => { view.value = 'list'; tab.value = 'channels' },
    })
    startPolling(chId)
  }
}

// ── 채널 생성 폼 멤버 관리 ────────────────────────────────────────────
function addMemberToForm(emp) {
  if (!newCh.value.members.find((m) => m.employeeid === emp.employeeid)) {
    newCh.value.members.push(emp)
  }
  memberSearch.value = ''
  showMemberDrop.value = false
}
function removeMember(emp) {
  newCh.value.members = newCh.value.members.filter((m) => m.employeeid !== emp.employeeid)
}
function hideMemberDrop() { setTimeout(() => { showMemberDrop.value = false }, 150) }

async function doCreateChannel() {
  if (!newCh.value.name.trim()) return
  creatingLoading.value = true
  try {
    const ch = await store.createChannel({
      name: newCh.value.name,
      channel_type: newCh.value.channel_type,
      department: newCh.value.department || null,
      team: newCh.value.team || null,
      member_ids: newCh.value.members.map((m) => m.employeeid),
    })
    newCh.value = { name: '', channel_type: 'team', department: '', team: '', members: [] }
    creating.value = false
    await openChannel(ch)
  } catch (e) {
    alert(e.response?.data?.detail || '채널 생성에 실패했습니다.')
  } finally {
    creatingLoading.value = false
  }
}

// ── 채팅 중 멤버 추가 ───────────────────────────────────────────────
function hideAddMemberDrop() { setTimeout(() => { showAddMemberDrop.value = false }, 150) }

async function doAddMember(emp) {
  addMemberSearch.value = ''
  showAddMemberDrop.value = false
  if (!store.activeChannel) return
  try {
    await store.addMember(store.activeChannel.id, emp.employeeid)
    addMemberOpen.value = false
  } catch (e) {
    alert(e.response?.data?.detail || '멤버 추가에 실패했습니다.')
  }
}

// ── 채널 삭제 ────────────────────────────────────────────────────────
async function confirmDeleteChannel() {
  if (!confirm(`"${channelDisplayName.value}" 채널을 삭제하시겠습니까?\n모든 메시지가 삭제됩니다.`)) return
  try {
    stopPolling()
    store.disconnectWS()
    await store.deleteChannel(store.activeChannel.id)
    view.value = 'list'; tab.value = 'channels'
  } catch (e) {
    alert(e.response?.data?.detail || '삭제에 실패했습니다.')
  }
}

// ── 채널 나가기 ──────────────────────────────────────────────────────
async function confirmLeaveChannel() {
  const name = channelDisplayName.value
  if (!confirm(`"${name}" 채널에서 나가시겠습니까?`)) return
  try {
    stopPolling()
    store.disconnectWS()
    await store.leaveChannel(store.activeChannel.id)
    view.value = 'list'; tab.value = 'channels'
  } catch (e) {
    alert(e.response?.data?.detail || '나가기에 실패했습니다.')
  }
}

// ── 메시지 전송 ──────────────────────────────────────────────────────
async function sendMessage() {
  if (!newMessage.value.trim() || !canSendMessage.value) return
  const text = newMessage.value
  newMessage.value = ''
  await store.sendMessage(text)
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

watch(view, (v) => { if (v !== 'chat') { stopPolling(); store.disconnectWS() } })
onUnmounted(() => {
  stopPolling()
  store.disconnectWS()
  clearInterval(channelRefreshTimer)
})
</script>

<style scoped>
.messenger-fab {
  position: fixed; bottom: 28px; right: 28px;
  width: 52px; height: 52px;
  background: #2563eb; color: #fff;
  border: none; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
  box-shadow: 0 4px 16px rgba(37,99,235,0.35);
  z-index: 1100; cursor: pointer; transition: transform 0.2s;
}
.messenger-fab:hover { transform: scale(1.08); }
.messenger-fab.open { background: #1e40af; }
.fab-badge {
  position: absolute; top: -4px; right: -4px;
  background: #ef4444; color: #fff;
  font-size: 0.6rem; padding: 1px 5px; border-radius: 999px;
}

.messenger-window {
  position: fixed; bottom: 90px; right: 28px;
  width: 380px; height: 540px;
  background: #fff; border-radius: 14px;
  border: 1px solid #e5e7eb;
  z-index: 1099; display: flex; flex-direction: column; overflow: hidden;
}

.messenger-header {
  background: #2563eb; color: #fff; padding: 8px 14px;
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
}
.tab-btn {
  background: rgba(255,255,255,0.15); color: rgba(255,255,255,0.8);
  border: none; border-radius: 6px; padding: 4px 10px;
  font-size: 0.75rem; cursor: pointer; transition: background 0.15s;
}
.tab-btn.active { background: rgba(255,255,255,0.35); color: #fff; font-weight: 600; }
.tab-btn:hover:not(.active) { background: rgba(255,255,255,0.22); }

.messenger-body { flex: 1; overflow-y: auto; padding: 4px 0; }

.ch-group-label {
  padding: 6px 14px 2px; font-size: 0.68rem; font-weight: 700;
  color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;
}
.channel-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 14px;
  cursor: pointer; border-bottom: 1px solid #f8fafc; transition: background 0.1s;
}
.channel-item:hover { background: #f8fafc; }
.announcement-ch { border-left: 3px solid #f59e0b; }

.channel-icon {
  width: 34px; height: 34px; background: #e0e7ff; color: #2563eb;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 0.9rem;
}
.announcement-icon { background: #fef3c7; color: #d97706; }
.dm-icon { background: #d1fae5; color: #059669; }
.channel-icon-sm {
  width: 28px; height: 28px; background: #e0e7ff; color: #2563eb;
  border-radius: 6px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 0.8rem;
}

/* 직원 목록 */
.employee-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 14px;
  cursor: pointer; border-bottom: 1px solid #f8fafc; transition: background 0.1s;
}
.employee-item:hover { background: #f0f9ff; }
.emp-avatar {
  width: 34px; height: 34px; background: #2563eb; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}

/* 프로필 뷰 */
.profile-header {
  background: #2563eb; color: #fff; padding: 8px 14px;
  display: flex; align-items: center; flex-shrink: 0;
}
.profile-body {
  display: flex; flex-direction: column; align-items: center;
  padding: 28px 24px; text-align: center;
}
.profile-avatar {
  width: 72px; height: 72px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 2rem;
}

/* 채널 생성 폼 */
.create-form {
  padding: 12px 14px; background: #f8fafc; border-bottom: 1px solid #e5e7eb;
}

/* 멤버 검색 드롭다운 */
.member-drop {
  position: absolute; top: calc(100% + 2px); left: 0; right: 0;
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 6px; z-index: 10; overflow: hidden;
  max-height: 140px; overflow-y: auto;
}
.member-drop-item {
  display: flex; align-items: center; gap: 8px; padding: 6px 10px; cursor: pointer;
}
.member-drop-item:hover { background: #f0f9ff; }
.emp-avatar-sm {
  width: 24px; height: 24px; background: #2563eb; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}

.ch-unread-badge {
  background: #ef4444; color: #fff;
  font-size: 0.65rem; font-weight: 700;
  padding: 2px 6px; border-radius: 999px;
  flex-shrink: 0; min-width: 18px; text-align: center;
}

.create-channel-btn {
  padding: 10px 14px; cursor: pointer; border-top: 1px solid #f1f5f9;
  color: #2563eb; font-size: 0.82rem;
  display: flex; align-items: center; transition: background 0.1s; flex-shrink: 0;
}
.create-channel-btn:hover { background: #f0f9ff; }

/* 채팅 뷰 */
.messenger-chat-header {
  padding: 8px 10px; border-bottom: 1px solid #f1f5f9;
  display: flex; align-items: center; flex-shrink: 0;
}

/* 멤버 추가 패널 */
.add-member-panel {
  padding: 8px 12px; background: #f8fafc;
  border-bottom: 1px solid #e5e7eb; flex-shrink: 0;
}

.messages-area { overflow-y: auto; padding: 10px 12px; }

.msg-bubble {
  margin-bottom: 10px; display: flex; flex-direction: column; align-items: flex-start;
}
.msg-bubble.mine { align-items: flex-end; }
.msg-sender-name { font-size: 0.65rem; color: #64748b; margin-bottom: 2px; padding: 0 4px; }

.msg-row { display: flex; align-items: flex-end; gap: 4px; }
.msg-bubble.mine .msg-row { flex-direction: row-reverse; }

.msg-content {
  background: #f1f5f9; border-radius: 12px 12px 12px 2px;
  padding: 6px 12px; font-size: 0.82rem; max-width: 72%; word-break: break-word;
}
.msg-bubble.mine .msg-content {
  background: #2563eb; color: #fff; border-radius: 12px 12px 2px 12px;
}

.unread-badge {
  font-size: 0.65rem; color: #f59e0b; font-weight: 700;
  line-height: 1; padding-bottom: 2px; white-space: nowrap;
}

.msg-time { font-size: 0.65rem; color: #94a3b8; margin-top: 2px; padding: 0 4px; }

.messenger-input {
  display: flex; padding: 8px 10px; border-top: 1px solid #f1f5f9; flex-shrink: 0;
}
</style>
