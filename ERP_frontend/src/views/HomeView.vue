<template>
  <div class="home-grid">

    <!-- ── Left Column ────────────────────────────────────── -->
    <div class="left-col">
      <!-- Profile Card -->
      <div class="card erp-card mb-4">
        <div class="card-body text-center py-4">
          <div class="profile-avatar mx-auto mb-3">{{ userInitial }}</div>
          <h6 class="fw-bold mb-0">{{ userName }}</h6>
          <p class="text-muted small mb-3">{{ user?.title || '직원' }}</p>
          <div class="d-flex justify-content-around text-center border-top pt-3">
            <div>
              <div class="fw-bold text-primary fs-5">{{ todayTaskCount }}</div>
              <div class="text-muted" style="font-size:0.72rem">오늘 일정</div>
            </div>
            <div class="border-start border-end px-3">
              <div class="fw-bold text-success fs-5">{{ tasks.length }}</div>
              <div class="text-muted" style="font-size:0.72rem">진행 업무</div>
            </div>
            <div>
              <div class="fw-bold text-warning fs-5">{{ notifications.length }}</div>
              <div class="text-muted" style="font-size:0.72rem">알림</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Memo Widget -->
      <div class="card erp-card">
        <div class="card-header d-flex align-items-center justify-content-between py-2">
          <span class="fw-semibold small"><i class="bi bi-journal-text me-1 text-warning"></i>메모</span>
          <button class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size:0.75rem" @click="memoExpanded = true">전체 보기</button>
        </div>
        <div class="card-body p-2">
          <div v-if="memosLoading" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
          <template v-else>
            <!-- 고정된 메모 가로 스크롤 -->
            <div v-if="pinnedMemos.length > 0" class="pinned-memos-scroll">
              <div v-for="(memo, idx) in pinnedMemos" :key="memo.id" :class="['pinned-memo-card', memoColorClass(idx)]">
                <div class="d-flex justify-content-between align-items-start mb-1">
                  <i class="bi bi-star-fill text-warning" style="font-size:0.7rem;cursor:pointer" @click="togglePin(memo)"></i>
                  <span class="text-muted" style="font-size:0.6rem">{{ fmtMemoDate(memo.updated_at) }}</span>
                </div>
                <div class="small pinned-memo-content">{{ memo.content || '(내용 없음)' }}</div>
              </div>
            </div>
            <div v-else class="text-muted small text-center py-4">
              <i class="bi bi-pin-angle fs-4 d-block mb-1"></i>고정된 메모가 없습니다
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ── Center Column ──────────────────────────────────── -->
    <div class="center-col">
      <!-- Calendar mini -->
      <div class="card erp-card mb-4">
        <div class="card-header d-flex align-items-center justify-content-between py-2">
          <span class="fw-semibold small"><i class="bi bi-calendar3 me-1 text-primary"></i>캘린더</span>
          <RouterLink to="/calendar" class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size:0.75rem">전체 보기</RouterLink>
        </div>
        <div class="card-body p-3">
          <div class="mini-calendar">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <button class="btn btn-sm btn-light px-2 py-1" @click="prevMonth"><i class="bi bi-chevron-left"></i></button>
              <span class="small fw-bold">{{ calendarTitle }}</span>
              <button class="btn btn-sm btn-light px-2 py-1" @click="nextMonth"><i class="bi bi-chevron-right"></i></button>
            </div>
            <div class="cal-grid mb-2">
              <div v-for="d in ['일','월','화','수','목','금','토']" :key="d" class="cal-head">{{ d }}</div>
              <div
                v-for="cell in calendarCells"
                :key="cell.key"
                class="cal-cell"
                :class="{ 'other-month': !cell.inMonth, 'has-event': cell.hasEvent }"
              >
                <span class="cal-num" :class="{ today: cell.isToday }">{{ cell.day }}</span>
              </div>
            </div>
            <div>
              <div v-for="ev in upcomingEvents.slice(0,4)" :key="ev.id" class="event-chip mb-1 d-flex align-items-center">
                <span class="event-dot me-2"></span>
                <span class="text-truncate">{{ ev.title || ev.summary }}</span>
              </div>
              <div v-if="upcomingEvents.length === 0" class="text-muted small text-center py-2">등록된 일정이 없습니다</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow panel -->
      <div class="card erp-card">
        <div class="card-header d-flex align-items-center justify-content-between py-2">
          <span class="fw-semibold small"><i class="bi bi-kanban me-1 text-primary"></i>진행 중인 업무</span>
          <RouterLink to="/workflow" class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size:0.75rem">워크플로우</RouterLink>
        </div>
        <div class="card-body p-3">
          <div v-if="tasksLoading" class="text-center py-4">
            <span class="spinner-border spinner-border-sm text-primary"></span>
          </div>
          <div v-else>
            <div
              v-for="task in tasks.slice(0, 6)"
              :key="task.id"
              class="task-item d-flex align-items-center gap-2 mb-2 p-2 rounded"
            >
              <span :class="['badge', statusBadge(task.status)]" style="font-size:0.65rem;min-width:52px;text-align:center">
                {{ statusLabel(task.status) }}
              </span>
              <span class="small text-truncate flex-grow-1">{{ task.title }}</span>
              <span class="text-muted" style="font-size:0.72rem">{{ formatDate(task.due_date) }}</span>
            </div>
            <div v-if="tasks.length === 0" class="text-muted small text-center py-3">
              <i class="bi bi-inbox fs-3 d-block mb-2"></i>진행 중인 업무가 없습니다
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Right Column ───────────────────────────────────── -->
    <div class="right-col">
      <!-- Attendance Panel -->
      <div class="card erp-card mb-4">
        <div class="card-header py-2 d-flex align-items-center justify-content-between">
          <span class="fw-semibold small"><i class="bi bi-clock-history me-1 text-success"></i>근태</span>
          <RouterLink to="/attendance" class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size:0.75rem">상세</RouterLink>
        </div>
        <div class="card-body py-3 px-3">
          <div class="text-center mb-3">
            <div class="fw-bold" style="font-size:1.6rem;letter-spacing:0.05em;color:#1e293b">{{ currentTime }}</div>
            <div class="text-muted small">{{ todayString }}</div>
          </div>

          <!-- 출퇴근 버튼 -->
          <div class="d-flex gap-2 mb-3">
            <button
              class="btn btn-sm flex-grow-1 fw-semibold"
              :class="checkinTime ? 'btn-success' : 'btn-outline-success'"
              @click="doCheckIn"
              :disabled="!!checkinTime || savingAttendance"
            >
              <i class="bi bi-box-arrow-in-right me-1"></i>
              <span v-if="savingAttendance && !checkinTime" class="spinner-border spinner-border-sm me-1"></span>
              {{ checkinTime ? checkinTime : '출근' }}
            </button>
            <button
              class="btn btn-sm flex-grow-1 fw-semibold"
              :class="checkoutTime ? 'btn-secondary' : 'btn-outline-secondary'"
              @click="doCheckOut"
              :disabled="!checkinTime || savingAttendance"
              :title="checkoutTime ? '클릭하여 퇴근 시간 수정' : ''"
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              <span v-if="savingAttendance && checkinTime" class="spinner-border spinner-border-sm me-1"></span>
              {{ checkoutTime ? checkoutTime + ' ✎' : '퇴근' }}
            </button>
          </div>

          <!-- 출근/퇴근 시간 표시 -->
          <div class="row g-2 text-center mb-3">
            <div class="col-6">
              <div class="p-2 rounded" :class="checkinTime ? 'bg-success bg-opacity-10' : 'bg-light'">
                <div class="fw-bold small" :class="checkinTime ? 'text-success' : 'text-muted'">출근</div>
                <div class="fw-semibold" style="font-size:0.85rem">{{ checkinTime || '--:--' }}</div>
              </div>
            </div>
            <div class="col-6">
              <div class="p-2 rounded" :class="checkoutTime ? 'bg-secondary bg-opacity-10' : 'bg-light'">
                <div class="fw-bold small" :class="checkoutTime ? 'text-secondary' : 'text-muted'">퇴근 <span v-if="checkoutTime" class="text-muted fw-normal" style="font-size:0.65rem">(재클릭 가능)</span></div>
                <div class="fw-semibold" style="font-size:0.85rem">{{ checkoutTime || '--:--' }}</div>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-between small mb-1">
            <span class="text-muted">주간 누적</span>
            <span class="fw-semibold">{{ weeklyHours }}</span>
          </div>
          <div class="progress mb-2" style="height:6px">
            <div class="progress-bar bg-success" :style="`width:${weeklyProgress}%`"></div>
          </div>
          <div>
            <span class="badge" :class="checkinTime ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border border-secondary-subtle'">
              {{ checkinTime ? (checkoutTime ? '퇴근 완료' : '근무 중') : '미출근' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Notifications -->
      <div class="card erp-card">
        <div class="card-header d-flex align-items-center justify-content-between py-2">
          <span class="fw-semibold small"><i class="bi bi-bell me-1 text-danger"></i>알림</span>
          <span v-if="notifications.length" class="badge bg-danger rounded-pill">{{ notifications.length }}</span>
        </div>
        <div class="card-body p-2">
          <div v-if="notifications.length === 0" class="text-muted small text-center py-4">
            <i class="bi bi-bell-slash fs-3 d-block mb-2"></i>새 알림이 없습니다
          </div>
          <div v-for="n in notifications.slice(0, 6)" :key="n.id" class="notif-item p-2 rounded mb-1">
            <div class="small fw-semibold text-truncate">{{ n.message || n.title || '알림' }}</div>
            <div class="text-muted text-truncate" style="font-size:0.72rem">{{ n.redirect_url || n.content }}</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- ── Memo Expanded Overlay (홈 화면 레이아웃은 그대로 두고 메모만 확장) ── -->
  <Teleport to="body">
    <div v-if="memoExpanded" class="memo-overlay-backdrop" @click.self="memoExpanded = false">
      <div class="memo-expanded-panel shadow-lg">
        <div class="memo-expanded-header">
          <span class="fw-bold"><i class="bi bi-journal-text me-2 text-warning"></i>메모</span>
          <button class="btn-close-memo" @click="memoExpanded = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="d-flex align-items-center justify-content-between px-3 py-2 border-bottom">
          <span class="small text-muted">전체 메모 <strong>{{ memos.length }}</strong></span>
          <div class="position-relative">
            <i class="bi bi-search position-absolute" style="left:8px;top:7px;font-size:0.7rem;color:#94a3b8"></i>
            <input v-model="memoSearch" class="form-control form-control-sm" style="padding-left:24px;font-size:0.75rem;width:150px" placeholder="검색" />
          </div>
        </div>
        <div class="memo-expanded-body">
          <div v-for="(memo, idx) in filteredMemos" :key="memo.id" :class="['memo-grid-card', memoColorClass(idx)]">
            <!-- 핀 버튼: 우측 상단 -->
            <div class="d-flex justify-content-end mb-1">
              <button
                class="btn-pin"
                :class="{ pinned: memo.is_pinned }"
                :title="memo.is_pinned ? '고정 해제' : '고정'"
                @click="togglePin(memo)"
              >
                <i class="bi" :class="memo.is_pinned ? 'bi-pin-fill' : 'bi-pin'"></i>
              </button>
            </div>
            <textarea
              v-model="memo.content"
              class="memo-grid-textarea"
              rows="4"
              placeholder="메모를 입력하세요..."
              @blur="updateMemoContent(memo)"
            ></textarea>
            <div class="d-flex justify-content-between align-items-center mt-2">
              <span class="text-muted" style="font-size:0.65rem">{{ fmtMemoDate(memo.updated_at) }}</span>
              <i class="bi bi-trash text-danger" style="cursor:pointer;font-size:0.8rem" @click="removeMemo(memo)"></i>
            </div>
          </div>
          <div v-if="filteredMemos.length === 0" class="text-muted small text-center py-5 w-100">메모가 없습니다</div>
        </div>
        <div class="memo-expanded-footer">
          <!-- 메모 생성 폼 -->
          <div v-if="showNewMemoForm" class="memo-create-form">
            <textarea
              v-model="newMemoContent"
              class="form-control form-control-sm mb-2"
              rows="3"
              placeholder="메모 내용을 입력하세요..."
              style="font-size:0.8rem;resize:none"
            ></textarea>
            <div class="d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showNewMemoForm = false; newMemoContent = ''">취소</button>
              <button class="btn btn-sm btn-warning flex-grow-1 fw-semibold" @click="submitNewMemo">
                <i class="bi bi-check-lg me-1"></i>저장
              </button>
            </div>
          </div>
          <button v-else class="btn btn-sm btn-warning w-100 fw-semibold" @click="showNewMemoForm = true">
            <i class="bi bi-plus-lg me-1"></i>새 메모 추가
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorksStore } from '@/stores/works'
import { worksApi } from '@/api/works'
import { attendanceApi } from '@/api/employees'

const authStore = useAuthStore()
const worksStore = useWorksStore()

// ── 메모 (API 기반, 다건) ──────────────────────────────────
const memos = ref([])
const memosLoading = ref(false)
const memoExpanded = ref(false)
const memoSearch = ref('')
const showNewMemoForm = ref(false)
const newMemoContent = ref('')

// 홈 화면에는 고정된 메모만 노출
const pinnedMemos = computed(() => memos.value.filter((m) => m.is_pinned))
// 전체보기(확장) 패널에는 검색어로 필터링된 전체 메모 노출
const filteredMemos = computed(() => {
  if (!memoSearch.value.trim()) return memos.value
  const q = memoSearch.value.toLowerCase()
  return memos.value.filter((m) => (m.content || '').toLowerCase().includes(q))
})

const MEMO_COLORS = ['memo-yellow', 'memo-mint', 'memo-purple']
function memoColorClass(idx) { return MEMO_COLORS[idx % MEMO_COLORS.length] }

function fmtMemoDate(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('ko-KR') } catch { return d }
}

async function loadMemos() {
  memosLoading.value = true
  try {
    const res = await worksApi.memos()
    memos.value = res.data
  } catch {
    memos.value = []
  } finally {
    memosLoading.value = false
  }
}

async function togglePin(memo) {
  const next = !memo.is_pinned
  memo.is_pinned = next
  try {
    await worksApi.togglePinMemo(memo.id, next)
  } catch {
    memo.is_pinned = !next
  }
}

async function updateMemoContent(memo) {
  if (!memo.id) return
  try { await worksApi.updateMemo(memo.id, memo.content) } catch {}
}

async function submitNewMemo() {
  const content = newMemoContent.value.trim()
  if (!content) return
  try {
    const res = await worksApi.createMemo(content)
    memos.value.unshift(res.data)
    newMemoContent.value = ''
    showNewMemoForm.value = false
  } catch {}
}

async function removeMemo(memo) {
  if (memo.id) {
    try { await worksApi.deleteMemo(memo.id) } catch {}
  }
  memos.value = memos.value.filter((m) => m !== memo)
}

// ── 인증 / 사용자 ────────────────────────────────────────
const user = computed(() => authStore.user)
const userName = computed(() => user.value ? `${user.value.lastname || ''}${user.value.firstname || ''}` : '')
const userInitial = computed(() => userName.value.charAt(0) || 'U')

// ── Works ────────────────────────────────────────────────
const tasks = computed(() => worksStore.tasks)
const tasksLoading = computed(() => worksStore.loading)
const notifications = computed(() => worksStore.notifications)
const calendarEvents = computed(() => worksStore.calendarEvents)
const todayTaskCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return worksStore.calendarEvents.filter((e) => (e.start_time || e.start || '').startsWith(today)).length
})

// ── 미니 캘린더 ──────────────────────────────────────────
const calendarDate = ref(new Date())
const calendarTitle = computed(() => `${calendarDate.value.getFullYear()}년 ${calendarDate.value.getMonth() + 1}월`)

const calendarCells = computed(() => {
  const year = calendarDate.value.getFullYear()
  const month = calendarDate.value.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = new Date()
  const eventDays = new Set(
    calendarEvents.value.map((e) => {
      const d = new Date(e.start_time || e.start || e.date)
      if (d.getFullYear() === year && d.getMonth() === month) return d.getDate()
      return null
    }).filter(Boolean),
  )
  const cells = []
  const prevDays = new Date(year, month, 0).getDate()
  for (let i = firstDay - 1; i >= 0; i--) {
    cells.push({ key: `p${i}`, day: prevDays - i, inMonth: false, isToday: false, hasEvent: false })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear()
    cells.push({ key: `c${d}`, day: d, inMonth: true, isToday, hasEvent: eventDays.has(d) })
  }
  let n = 1
  while (cells.length % 7 !== 0) cells.push({ key: `n${n}`, day: n++, inMonth: false, isToday: false, hasEvent: false })
  return cells
})

const upcomingEvents = computed(() =>
  calendarEvents.value
    .filter((e) => new Date(e.start_time || e.start || e.date) >= new Date())
    .sort((a, b) => new Date(a.start_time || a.start || a.date) - new Date(b.start_time || b.start || b.date))
    .slice(0, 4),
)

function prevMonth() { calendarDate.value = new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth() - 1, 1) }
function nextMonth() { calendarDate.value = new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth() + 1, 1) }

// ── 근태 (API 기반) ────────────────────────────────────
const todayRecord = ref(null)
const weeklyMinutes = ref(0)
const savingAttendance = ref(false)
const currentTime = ref('')
const todayString = ref('')
let clockTimer = null

const checkinTime = computed(() => todayRecord.value?.checkin_time?.slice(0, 5) || '')
const checkoutTime = computed(() => todayRecord.value?.checkout_time?.slice(0, 5) || '')

async function loadAttendance() {
  try {
    const res = await attendanceApi.today()
    todayRecord.value = res.data
  } catch {
    todayRecord.value = null
  }
  // 주간 누적 시간 계산을 위해 이번 달 기록 로드
  try {
    const m = new Date().toISOString().slice(0, 7)
    const res = await attendanceApi.list(m)
    const d = new Date()
    const day = d.getDay()
    const monday = new Date(d)
    monday.setDate(d.getDate() - (day === 0 ? 6 : day - 1))
    const weekStart = monday.toISOString().slice(0, 10)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    const weekEnd = sunday.toISOString().slice(0, 10)
    let total = 0
    res.data.filter(r => r.date >= weekStart && r.date <= weekEnd).forEach(rec => {
      if (rec.checkin_time && rec.checkout_time) {
        const [ih, im] = rec.checkin_time.split(':').map(Number)
        const [oh, om] = rec.checkout_time.split(':').map(Number)
        const diff = (oh * 60 + om) - (ih * 60 + im)
        if (diff > 0) total += diff
      }
    })
    weeklyMinutes.value = total
  } catch {
    weeklyMinutes.value = 0
  }
}

async function doCheckIn() {
  if (checkinTime.value || savingAttendance.value) return
  savingAttendance.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkin(time)
    todayRecord.value = res.data
    await loadAttendance()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data || '출근 처리에 실패했습니다.'
    alert(String(msg))
  } finally {
    savingAttendance.value = false
  }
}

async function doCheckOut() {
  if (!checkinTime.value || savingAttendance.value) return
  savingAttendance.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkout(time)
    todayRecord.value = res.data
    await loadAttendance()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data || '퇴근 처리에 실패했습니다.'
    alert(String(msg))
  } finally {
    savingAttendance.value = false
  }
}

const weeklyHours = computed(() => {
  if (weeklyMinutes.value === 0) return '0h 0m'
  return `${Math.floor(weeklyMinutes.value / 60)}h ${weeklyMinutes.value % 60}m`
})

const weeklyProgress = computed(() => {
  return Math.min(100, Math.round((weeklyMinutes.value / (40 * 60)) * 100))
})

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  todayString.value = now.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
}

// ── 유틸 ─────────────────────────────────────────────────
function statusBadge(status) {
  const map = { TODO: 'bg-secondary', IN_PROGRESS: 'bg-primary', DONE: 'bg-success', '진행중': 'bg-primary', '완료': 'bg-success', '대기': 'bg-secondary', '지연': 'bg-danger' }
  return map[status] || 'bg-secondary'
}
function statusLabel(status) {
  const map = { TODO: '대기', IN_PROGRESS: '진행중', DONE: '완료', '진행중': '진행중', '완료': '완료', '대기': '대기', '지연': '지연' }
  return map[status] || status
}
function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' })
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loadAttendance()
  loadMemos()
  worksStore.fetchTasks().catch(() => {})
  worksStore.fetchCalendarEvents().catch(() => {})
  worksStore.fetchNotifications().catch(() => {})
})

onUnmounted(() => clearInterval(clockTimer))
</script>

<style scoped>
.home-grid {
  display: grid;
  grid-template-columns: 270px 1fr 290px;
  gap: 20px;
  min-height: calc(100vh - var(--navbar-height) - 48px);
  align-items: start;
}

.erp-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.erp-card .card-header {
  background: #fff;
  border-bottom: 1px solid #f1f5f9;
  border-radius: 12px 12px 0 0;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.6rem;
  box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 3px;
  font-size: 0.72rem;
}
.cal-head {
  text-align: center;
  color: #94a3b8;
  padding: 3px 0;
  font-weight: 600;
}
.cal-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  cursor: default;
  color: #374151;
  position: relative;
}
.cal-cell.other-month { color: #d1d5db; }
.cal-num {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.cal-num.today { background: #2563eb; color: #fff; font-weight: 700; }
.cal-cell.has-event::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #f59e0b;
  border-radius: 50%;
}

.event-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #2563eb;
  border-radius: 50%;
  flex-shrink: 0;
}
.event-chip {
  font-size: 0.78rem;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 3px 6px;
  background: #f8fafc;
  border-radius: 4px;
}

.task-item {
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  transition: border-color 0.1s;
}
.task-item:hover { border-color: #e0e7ff; }

.notif-item {
  background: #f8fafc;
  border-left: 3px solid #e5e7eb;
}

/* ── 메모 (홈 위젯: 고정된 메모 가로 스크롤) ──────────────── */
.pinned-memos-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: #e2e8f0 transparent;
}
.pinned-memos-scroll::-webkit-scrollbar { height: 4px; }
.pinned-memos-scroll::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 2px; }

.pinned-memo-card {
  flex-shrink: 0;
  width: 150px;
  padding: 8px 10px;
  border-radius: 8px;
}
.pinned-memo-content {
  color: #374151;
  font-size: 0.78rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.memo-yellow { background: #fef9c3; border: 1px solid #fde68a; }
.memo-mint   { background: #ccfbf1; border: 1px solid #99f6e4; }
.memo-purple { background: #ede9fe; border: 1px solid #ddd6fe; }

/* ── 메모 확장 오버레이 ──────────────────────────────────── */
.memo-overlay-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.memo-expanded-panel {
  width: 420px;
  max-height: 82vh;
  background: #fff;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.memo-expanded-header {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
}
.btn-close-memo {
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 0.9rem;
  cursor: pointer;
  line-height: 1;
}
.btn-close-memo:hover { color: #475569; }

.memo-expanded-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  align-content: start;
}
.memo-grid-card {
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
}
.memo-grid-textarea {
  resize: none;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.78rem;
  color: #374151;
  width: 100%;
}
.memo-expanded-footer {
  padding: 10px 14px;
  border-top: 1px solid #f1f5f9;
}
.memo-create-form {
  padding: 4px 0;
}

/* 핀 버튼 */
.btn-pin {
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.15s, background 0.15s;
}
.btn-pin:hover { color: #f59e0b; background: rgba(245,158,11,0.1); }
.btn-pin.pinned { color: #f59e0b; }
</style>
