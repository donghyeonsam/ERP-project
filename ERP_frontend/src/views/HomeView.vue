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
          <RouterLink to="/memo" class="btn btn-sm btn-outline-secondary py-0 px-2" style="font-size:0.75rem">전체 보기</RouterLink>
        </div>
        <div class="card-body p-3">
          <textarea
            v-model="memoText"
            class="form-control border-0 bg-light"
            rows="8"
            placeholder="메모를 입력하세요..."
            style="resize:none;font-size:0.85rem;border-radius:8px"
          ></textarea>
          <button class="btn btn-sm btn-warning mt-2 w-100 fw-semibold" @click="saveMemo" :disabled="memoSaving">
            <span v-if="memoSaving" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-floppy me-1"></i>저장
          </button>
          <div v-if="memoSaved" class="text-success small text-center mt-1">
            <i class="bi bi-check-circle me-1"></i>저장되었습니다
          </div>
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
                :class="{ 'other-month': !cell.inMonth, today: cell.isToday, 'has-event': cell.hasEvent }"
              >{{ cell.day }}</div>
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
              :disabled="!!checkinTime"
            >
              <i class="bi bi-box-arrow-in-right me-1"></i>
              {{ checkinTime ? checkinTime : '출근' }}
            </button>
            <button
              class="btn btn-sm flex-grow-1 fw-semibold"
              :class="checkoutTime ? 'btn-secondary' : 'btn-outline-secondary'"
              @click="doCheckOut"
              :disabled="!checkinTime || !!checkoutTime"
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              {{ checkoutTime ? checkoutTime : '퇴근' }}
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
                <div class="fw-bold small" :class="checkoutTime ? 'text-secondary' : 'text-muted'">퇴근</div>
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
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorksStore } from '@/stores/works'
import { worksApi } from '@/api/works'

const authStore = useAuthStore()
const worksStore = useWorksStore()

// ── 메모 (API 기반) ──────────────────────────────────────
const memoText = ref('')
const memoId = ref(null)
const memoSaving = ref(false)
const memoSaved = ref(false)

async function loadMemo() {
  try {
    const res = await worksApi.memos()
    if (res.data.length > 0) {
      memoId.value = res.data[0].id
      memoText.value = res.data[0].content
    }
  } catch {
    memoText.value = localStorage.getItem('erp_memo') || ''
  }
}

async function saveMemo() {
  memoSaving.value = true
  memoSaved.value = false
  try {
    if (memoId.value) {
      await worksApi.updateMemo(memoId.value, memoText.value)
    } else {
      const res = await worksApi.createMemo(memoText.value)
      memoId.value = res.data.id
    }
    memoSaved.value = true
    setTimeout(() => { memoSaved.value = false }, 2000)
  } catch {
    localStorage.setItem('erp_memo', memoText.value)
    memoSaved.value = true
    setTimeout(() => { memoSaved.value = false }, 2000)
  } finally {
    memoSaving.value = false
  }
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

// ── 근태 (localStorage 기반) ────────────────────────────
const checkinTime = ref('')
const checkoutTime = ref('')
const currentTime = ref('')
const todayString = ref('')
let clockTimer = null

function loadAttendance() {
  const today = new Date().toISOString().slice(0, 10)
  const saved = JSON.parse(localStorage.getItem('erp_attendance') || '{}')
  if (saved.date === today) {
    checkinTime.value = saved.checkin || ''
    checkoutTime.value = saved.checkout || ''
  }
}

function saveAttendance() {
  localStorage.setItem('erp_attendance', JSON.stringify({
    date: new Date().toISOString().slice(0, 10),
    checkin: checkinTime.value,
    checkout: checkoutTime.value,
  }))
}

function doCheckIn() {
  if (checkinTime.value) return
  checkinTime.value = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  saveAttendance()
}

function doCheckOut() {
  if (!checkinTime.value || checkoutTime.value) return
  checkoutTime.value = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  saveAttendance()
}

const weeklyHours = computed(() => {
  if (!checkinTime.value || !checkoutTime.value) return '-- h'
  try {
    const [ih, im] = checkinTime.value.split(':').map(Number)
    const [oh, om] = checkoutTime.value.split(':').map(Number)
    const diff = (oh * 60 + om) - (ih * 60 + im)
    return `${Math.floor(diff / 60)}h ${diff % 60}m`
  } catch { return '-- h' }
})

const weeklyProgress = computed(() => {
  if (!checkinTime.value || !checkoutTime.value) return 0
  try {
    const [ih, im] = checkinTime.value.split(':').map(Number)
    const [oh, om] = checkoutTime.value.split(':').map(Number)
    const diff = (oh * 60 + om) - (ih * 60 + im)
    return Math.min(100, Math.round((diff / 480) * 100))
  } catch { return 0 }
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
  loadMemo()
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
  gap: 2px;
  font-size: 0.72rem;
}
.cal-head {
  text-align: center;
  color: #94a3b8;
  padding: 3px 0;
  font-weight: 600;
}
.cal-cell {
  text-align: center;
  padding: 4px 0;
  border-radius: 4px;
  cursor: default;
  color: #374151;
}
.cal-cell.other-month { color: #d1d5db; }
.cal-cell.today { background: #2563eb; color: #fff; font-weight: 700; border-radius: 50%; }
.cal-cell.has-event::after {
  content: '';
  display: block;
  width: 4px;
  height: 4px;
  background: #f59e0b;
  border-radius: 50%;
  margin: 1px auto 0;
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
</style>
