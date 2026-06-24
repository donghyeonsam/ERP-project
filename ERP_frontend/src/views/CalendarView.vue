<template>
  <div class="calendar-layout">
    <!-- ── 좌측 패널 ──────────────────────────────────────────────── -->
    <aside class="cal-left-panel">
      <button class="btn btn-outline-secondary w-100 mb-4 fw-semibold" @click="openCreate">
        <i class="bi bi-plus-lg me-1"></i>일정등록
      </button>

      <!-- 미니 캘린더 네비게이터 -->
      <div class="mini-cal mb-4">
        <div class="d-flex justify-content-between align-items-center mb-2 px-1">
          <button class="btn btn-sm btn-light px-2 py-0" @click="miniPrev"><i class="bi bi-chevron-left" style="font-size:0.7rem"></i></button>
          <span class="small fw-bold">{{ miniTitle }}</span>
          <button class="btn btn-sm btn-light px-2 py-0" @click="miniNext"><i class="bi bi-chevron-right" style="font-size:0.7rem"></i></button>
        </div>
        <div class="mini-grid">
          <div v-for="d in ['일','월','화','수','목','금','토']" :key="d" class="mini-head">{{ d }}</div>
          <div
            v-for="cell in miniCells"
            :key="cell.key"
            class="mini-cell"
            :class="{ 'other-month': !cell.inMonth, today: cell.isToday, selected: cell.isSelected, 'has-event': cell.hasEvent }"
            @click="selectDate(cell)"
          >{{ cell.day }}</div>
        </div>
      </div>

      <!-- 내 캘린더 -->
      <div class="cal-section mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="cal-section-title">내 캘린더</span>
          <button class="btn-icon" @click="showMyCalCreate = !showMyCalCreate"><i class="bi bi-pencil-square" style="font-size:0.75rem"></i></button>
        </div>
        <div class="cal-check-item">
          <label class="d-flex align-items-center gap-2 small" style="cursor:pointer">
            <input type="checkbox" v-model="showTaskEvents" class="d-none" />
            <span class="cal-dot" :style="`background:${showTaskEvents ? '#16a34a' : '#ccc'};border-color:#16a34a`" @click="showTaskEvents = !showTaskEvents">
              <i v-if="showTaskEvents" class="bi bi-check text-white" style="font-size:0.6rem"></i>
            </span>
            업무 마감일 (Work)
          </label>
        </div>
        <div v-for="cal in myCalendars" :key="cal.id" class="cal-check-item">
          <label class="d-flex align-items-center gap-2 small" :style="`cursor:pointer`">
            <input type="checkbox" v-model="cal.visible" class="d-none" />
            <span class="cal-dot" :style="`background:${cal.color};border-color:${cal.color}`" @click="cal.visible = !cal.visible">
              <i v-if="cal.visible" class="bi bi-check text-white" style="font-size:0.6rem"></i>
            </span>
            {{ cal.name }}
          </label>
        </div>
        <div v-if="showMyCalCreate" class="mt-2 d-flex gap-1">
          <input v-model="newCalName" class="form-control form-control-sm" placeholder="캘린더 이름" style="font-size:0.75rem" />
          <button class="btn btn-sm btn-primary px-2" @click="addMyCalendar">추가</button>
        </div>
      </div>

      <!-- 전사 캘린더 -->
      <div class="cal-section">
        <div class="mb-2"><span class="cal-section-title">전사 캘린더</span></div>
        <div v-for="cal in companyCalendars" :key="cal.id" class="cal-check-item">
          <label class="d-flex align-items-center gap-2 small" style="cursor:pointer">
            <input type="checkbox" v-model="cal.visible" class="d-none" />
            <span class="cal-dot" :style="`background:${cal.visible ? cal.color : '#ccc'};border-color:${cal.color}`" @click="cal.visible = !cal.visible">
              <i v-if="cal.visible" class="bi bi-check text-white" style="font-size:0.6rem"></i>
            </span>
            {{ cal.name }}
          </label>
        </div>
      </div>
    </aside>

    <!-- ── 우측 메인 캘린더 ────────────────────────────────────────── -->
    <main class="cal-main">
      <!-- 상단 컨트롤 -->
      <div class="cal-header d-flex align-items-center gap-3 mb-3">
        <div class="d-flex align-items-center gap-1">
          <button class="btn btn-sm btn-outline-secondary px-2" @click="changeMonth(-1)"><i class="bi bi-chevron-left"></i></button>
          <button class="btn btn-sm btn-outline-secondary px-2" @click="changeMonth(1)"><i class="bi bi-chevron-right"></i></button>
          <button class="btn btn-sm btn-outline-secondary ms-1" @click="goToday">오늘</button>
        </div>
        <h6 class="mb-0 fw-bold flex-grow-1" style="font-size:1.1rem">{{ calTitle }}</h6>
        <div class="btn-group btn-group-sm" role="group">
          <button v-for="v in views" :key="v.key" class="btn btn-outline-secondary" :class="{ active: currentView === v.key }" @click="currentView = v.key">{{ v.label }}</button>
        </div>
      </div>

      <!-- 월간 뷰 -->
      <div v-if="currentView === 'month'" class="card erp-card">
        <div class="card-body p-0">
          <div class="cal-weeks-container">
            <!-- 요일 헤더 -->
            <div class="cal-header-row">
              <div v-for="d in dayHeaders" :key="d" class="cal-head-full">{{ d }}</div>
            </div>
            <!-- 주 단위 행 -->
            <div v-for="week in weeks" :key="week.id" class="cal-week-wrapper">
              <!-- 날짜 숫자 셀 -->
              <div class="cal-week-cells">
                <div
                  v-for="(cell, idx) in week.cells"
                  :key="cell.key"
                  class="cal-cell-full"
                  :class="{ 'other-month': !cell.inMonth, today: cell.isToday }"
                  @click="openCreateOnDate(cell.fullDate)"
                >
                  <div class="cal-day-num" :class="{ 'today-circle': cell.isToday }">{{ cell.day }}</div>
                  <div v-if="week.cellOverflow[idx] > 0" class="cal-overflow-badge">+{{ week.cellOverflow[idx] }}개</div>
                </div>
              </div>
              <!-- 일정 스팬 레이어 -->
              <div
                class="cal-event-layer"
                :style="{ minHeight: `${Math.max(1, week.maxVisibleRows) * 22 + 2}px` }"
              >
                <div
                  v-for="span in week.visibleSpans"
                  :key="span.id"
                  class="cal-event-span"
                  :class="{ 'span-start': span.isStart, 'span-end': span.isEnd }"
                  :style="{
                    gridColumnStart: span.startCol + 1,
                    gridColumnEnd: span.endCol + 2,
                    gridRowStart: span.row + 1,
                    background: eventBgColor(span.event),
                    color: eventTextColor(eventBgColor(span.event)),
                  }"
                  :title="span.event.title"
                  @click.stop="selectEvent(span.event)"
                >
                  <span v-if="span.isStart" class="event-span-title" :class="{ 'text-decoration-line-through': span.event.status === 'DONE' }">
                    <i v-if="span.event.source === 'task'" class="bi bi-kanban me-1" style="font-size:0.65rem;vertical-align:middle"></i>
                    <i v-else-if="span.event.is_all_day" class="bi bi-circle-fill me-1" style="font-size:0.35rem;vertical-align:middle"></i>
                    {{ span.event.title }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 목록 뷰 -->
      <div v-if="currentView === 'list'" class="card erp-card">
        <div class="card-header py-2"><span class="fw-semibold small">{{ calTitle }} 일정 목록</span></div>
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
          <div v-else-if="monthEvents.length === 0" class="text-center text-muted small py-5">
            <i class="bi bi-calendar-x fs-2 d-block mb-2"></i>등록된 일정이 없습니다
          </div>
          <div
            v-for="ev in monthEvents"
            :key="ev.id"
            class="event-row d-flex align-items-start gap-3 p-3 border-bottom"
            @click="selectEvent(ev)"
          >
            <div class="event-date-badge text-center">
              <div class="fw-bold" style="font-size:1.1rem">{{ evDay(ev) }}</div>
              <div class="text-muted small">{{ evMonth(ev) }}</div>
            </div>
            <div class="event-color-bar" :style="`background:${eventBgColor(ev)}`"></div>
            <div class="flex-grow-1">
              <div class="fw-semibold small" :class="{ 'text-decoration-line-through text-muted': ev.status === 'DONE' }">
                <i v-if="ev.source === 'task'" class="bi bi-kanban me-1 text-muted"></i>{{ ev.title }}
              </div>
              <div v-if="ev.description" class="text-muted" style="font-size:0.75rem">{{ ev.description }}</div>
              <div class="text-muted" style="font-size:0.72rem">
                <template v-if="ev.is_all_day">종일</template>
                <template v-else>{{ fmtTime(ev.start_time) }} – {{ fmtTime(ev.end_time) }}</template>
              </div>
            </div>
            <RouterLink
              v-if="ev.source === 'task'"
              :to="`/works/${ev.sourceId}`"
              class="btn btn-sm btn-outline-primary py-0 px-2 align-self-center"
              style="font-size:0.7rem"
              @click.stop
            >
              <i class="bi bi-box-arrow-up-right"></i>
            </RouterLink>
            <button v-else class="btn btn-sm btn-outline-danger py-0 px-2 align-self-center" style="font-size:0.7rem" @click.stop="deleteEvent(ev)">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- ── 일정 생성 모달 ──────────────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="showCreateModal" class="modal-backdrop-custom" @click.self="showCreateModal = false">
      <div class="modal-panel shadow-lg">
        <div class="modal-panel-header">
          <span class="fw-bold small"><i class="bi bi-calendar-plus me-2 text-primary"></i>일정 추가</span>
          <button class="btn-close-panel" @click="showCreateModal = false"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-panel-body">
          <div class="mb-3">
            <label class="form-label small fw-semibold">제목 <span class="text-danger">*</span></label>
            <input v-model="form.title" class="form-control form-control-sm" placeholder="일정 제목을 입력하세요" />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">설명</label>
            <textarea v-model="form.description" class="form-control form-control-sm" rows="2" placeholder="상세 내용 (선택)"></textarea>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-6">
              <label class="form-label small fw-semibold">시작</label>
              <input v-model="form.start_time" type="datetime-local" class="form-control form-control-sm" :disabled="form.is_all_day" />
            </div>
            <div class="col-6">
              <label class="form-label small fw-semibold">종료</label>
              <input v-model="form.end_time" type="datetime-local" class="form-control form-control-sm" :disabled="form.is_all_day" />
            </div>
          </div>
          <div class="mb-3 form-check">
            <input id="allDayCheck" v-model="form.is_all_day" type="checkbox" class="form-check-input" />
            <label for="allDayCheck" class="form-check-label small">종일 일정</label>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">색상</label>
            <div class="d-flex gap-2 flex-wrap">
              <button
                v-for="c in colorOptions"
                :key="c"
                class="color-btn"
                :style="`background:${c};outline: 3px solid ${form.color === c ? '#374151' : 'transparent'}`"
                @click="form.color = c"
              ></button>
            </div>
          </div>
          <div v-if="createError" class="alert alert-danger small py-2">{{ createError }}</div>
        </div>
        <div class="modal-panel-footer d-flex gap-2">
          <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showCreateModal = false">취소</button>
          <button class="btn btn-sm btn-primary flex-grow-1" :disabled="saving" @click="submitCreate">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            저장
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- ── 이벤트 상세 팝업 ────────────────────────────────────────────── -->
  <Teleport to="body">
    <div v-if="selectedEv" class="modal-backdrop-custom" @click.self="selectedEv = null">
      <div class="modal-panel shadow-lg" style="max-width:360px">
        <div class="modal-panel-header" :style="`background:${eventBgColor(selectedEv)};color:#fff`">
          <span class="fw-bold small">
            <i v-if="selectedEv.source === 'task'" class="bi bi-kanban me-1"></i>{{ selectedEv.title }}
          </span>
          <button class="btn-close-panel" style="color:#fff" @click="selectedEv = null"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-panel-body">
          <div v-if="selectedEv.source === 'task'" class="mb-2">
            <span class="badge bg-light text-dark border">Work 업무</span>
            <span v-if="selectedEv.status === 'DONE'" class="badge bg-success ms-1">완료</span>
          </div>
          <div class="mb-2 small">
            <i class="bi bi-clock me-2 text-muted"></i>
            <template v-if="selectedEv.is_all_day">종일</template>
            <template v-else>{{ fmtDatetime(selectedEv.start_time) }} – {{ fmtDatetime(selectedEv.end_time) }}</template>
          </div>
          <div v-if="selectedEv.description" class="small text-muted">
            <i class="bi bi-text-left me-2"></i>{{ selectedEv.description }}
          </div>
        </div>
        <div class="modal-panel-footer d-flex gap-2">
          <RouterLink v-if="selectedEv.source === 'task'" :to="`/works/${selectedEv.sourceId}`" class="btn btn-sm btn-outline-primary flex-grow-1">
            <i class="bi bi-box-arrow-up-right me-1"></i>업무 상세보기
          </RouterLink>
          <button v-else class="btn btn-sm btn-outline-danger flex-grow-1" @click="deleteEvent(selectedEv)">
            <i class="bi bi-trash me-1"></i>삭제
          </button>
          <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="selectedEv = null">닫기</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorksStore } from '@/stores/works'
import { useAuthStore } from '@/stores/auth'

const worksStore = useWorksStore()
const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const createError = ref('')

// ── 뷰 상태 ──────────────────────────────────────────────────────────
const currentView = ref('month')
const views = [
  { key: 'month', label: '월간' },
  { key: 'list', label: '목록' },
]

// ── 날짜 상태 ────────────────────────────────────────────────────────
const calDate = ref(new Date())
const miniDate = ref(new Date())
const selectedDate = ref(null)

const calTitle = computed(() => `${calDate.value.getFullYear()}년 ${calDate.value.getMonth() + 1}월`)
const miniTitle = computed(() => `${miniDate.value.getFullYear()}년 ${miniDate.value.getMonth() + 1}월`)
const dayHeaders = ['일', '월', '화', '수', '목', '금', '토']

// ── 캘린더 설정 ──────────────────────────────────────────────────────
const myCalendars = reactive([
  { id: 1, name: '내 일정(기본)', color: '#f59e0b', visible: true },
  { id: 2, name: '일정 확인', color: '#3b82f6', visible: true },
])
const companyCalendars = reactive([
  { id: 10, name: '전사일정', color: '#ef4444', visible: true },
])
const showMyCalCreate = ref(false)
const newCalName = ref('')

function addMyCalendar() {
  if (!newCalName.value.trim()) return
  const colors = ['#10b981', '#8b5cf6', '#f97316', '#06b6d4']
  myCalendars.push({ id: Date.now(), name: newCalName.value, color: colors[myCalendars.length % colors.length], visible: true })
  newCalName.value = ''
  showMyCalCreate.value = false
}

// ── 이벤트 데이터 ────────────────────────────────────────────────────
// Work관리(Task)의 마감일을 캘린더 일정으로 변환해 함께 표시 (캘린더 ↔ Work 연동)
const showTaskEvents = ref(true)
const TASK_PRIORITY_COLOR = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#64748b' }

const taskEvents = computed(() =>
  worksStore.tasks
    .filter((t) => t.due_date)
    .map((t) => ({
      id: `task-${t.id}`,
      title: t.title,
      description: t.content,
      start_time: `${t.due_date}T00:00:00`,
      end_time: `${t.due_date}T23:59:59`,
      is_all_day: true,
      color: TASK_PRIORITY_COLOR[t.priority] || '#16a34a',
      source: 'task',
      sourceId: t.id,
      status: t.status,
    }))
)

const events = computed(() => [
  ...worksStore.calendarEvents.map((e) => ({ ...e, source: 'event' })),
  ...(showTaskEvents.value ? taskEvents.value : []),
])

const monthEvents = computed(() => {
  const y = calDate.value.getFullYear(), m = calDate.value.getMonth()
  return events.value
    .filter((e) => {
      const d = new Date(e.start_time || e.start || e.date)
      return d.getFullYear() === y && d.getMonth() === m
    })
    .sort((a, b) => new Date(a.start_time || a.start) - new Date(b.start_time || b.start))
})

// ── 메인 캘린더 (주 단위 다중날짜 스팬) ─────────────────────────────
const MAX_EVENT_ROWS = 3

const weeks = computed(() => {
  const year = calDate.value.getFullYear()
  const month = calDate.value.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = new Date()

  // 플랫 셀 배열 구성
  const flatCells = []
  const prevDays = new Date(year, month, 0).getDate()
  for (let i = firstDay - 1; i >= 0; i--) {
    const d = prevDays - i
    const pm = month === 0 ? 11 : month - 1
    const py = month === 0 ? year - 1 : year
    flatCells.push({ key: `p${i}`, day: d, inMonth: false, isToday: false, fullDate: `${py}-${String(pm + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}` })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear()
    flatCells.push({ key: `c${d}`, day: d, inMonth: true, isToday, fullDate: `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}` })
  }
  let n = 1
  while (flatCells.length % 7 !== 0) {
    const nm = month === 11 ? 0 : month + 1
    const ny = month === 11 ? year + 1 : year
    flatCells.push({ key: `n${n}`, day: n, inMonth: false, isToday: false, fullDate: `${ny}-${String(nm + 1).padStart(2, '0')}-${String(n).padStart(2, '0')}` })
    n++
  }

  // 주 단위 그룹화 + 이벤트 슬롯 배분
  const result = []
  for (let w = 0; w < flatCells.length / 7; w++) {
    const weekCells = flatCells.slice(w * 7, w * 7 + 7)
    const weekStart = weekCells[0].fullDate
    const weekEnd = weekCells[6].fullDate

    // 이 주에 걸치는 이벤트 추출 (시작일 오름차순, 기간 긴 것 우선)
    const overlapping = events.value
      .filter((ev) => {
        const s = (ev.start_time || ev.start || ev.date || '').slice(0, 10)
        const e = (ev.end_time || ev.end || s).slice(0, 10)
        return s <= weekEnd && e >= weekStart
      })
      .sort((a, b) => {
        const as = (a.start_time || a.start || a.date || '').slice(0, 10)
        const bs = (b.start_time || b.start || b.date || '').slice(0, 10)
        if (as !== bs) return as.localeCompare(bs)
        const ae = (a.end_time || a.end || as).slice(0, 10)
        const be = (b.end_time || b.end || bs).slice(0, 10)
        return new Date(be) - new Date(ae)  // 긴 이벤트 우선
      })

    // 트랙(행) 배분: tracks[row] = 마지막 endCol
    const tracks = []
    const allSpans = []

    overlapping.forEach((ev) => {
      const evStart = (ev.start_time || ev.start || ev.date || '').slice(0, 10)
      const evEnd = (ev.end_time || ev.end || evStart).slice(0, 10)

      const startIdx = weekCells.findIndex(c => c.fullDate === evStart)
      const endIdx = weekCells.findIndex(c => c.fullDate === evEnd)
      const sc = evStart < weekStart ? 0 : (startIdx === -1 ? 0 : startIdx)
      const ec = evEnd > weekEnd ? 6 : (endIdx === -1 ? 6 : endIdx)

      // 빈 트랙 탐색
      let row = 0
      while (row < tracks.length && tracks[row] >= sc) row++
      tracks[row] = ec

      allSpans.push({
        id: `${ev.id}-w${w}`,
        event: ev,
        startCol: sc,
        endCol: ec,
        row,
        isStart: evStart >= weekStart,
        isEnd: evEnd <= weekEnd,
      })
    })

    // MAX_EVENT_ROWS 초과분 overflow 카운트 (셀별)
    const cellOverflow = Array(7).fill(0)
    const visibleSpans = []
    allSpans.forEach(span => {
      if (span.row >= MAX_EVENT_ROWS) {
        for (let col = span.startCol; col <= span.endCol; col++) {
          cellOverflow[col]++
        }
      } else {
        visibleSpans.push(span)
      }
    })

    result.push({
      id: w,
      cells: weekCells,
      visibleSpans,
      cellOverflow,
      maxVisibleRows: Math.min(MAX_EVENT_ROWS, tracks.length),
    })
  }
  return result
})

// ── 미니 캘린더 셀 ───────────────────────────────────────────────────
const miniCells = computed(() => {
  const year = miniDate.value.getFullYear(), month = miniDate.value.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = new Date()
  const eventDays = new Set(events.value.map((e) => {
    const d = new Date(e.start_time || e.start || e.date)
    if (d.getFullYear() === year && d.getMonth() === month) return d.getDate()
    return null
  }).filter(Boolean))

  const result = []
  const prevDays = new Date(year, month, 0).getDate()
  for (let i = firstDay - 1; i >= 0; i--) {
    result.push({ key: `mp${i}`, day: prevDays - i, inMonth: false, isToday: false, isSelected: false, hasEvent: false, fullDate: null })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear()
    const fd = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const isSelected = selectedDate.value === fd
    result.push({ key: `mc${d}`, day: d, inMonth: true, isToday, isSelected, hasEvent: eventDays.has(d), fullDate: fd })
  }
  let n = 1
  while (result.length % 7 !== 0) {
    result.push({ key: `mn${n}`, day: n++, inMonth: false, isToday: false, isSelected: false, hasEvent: false, fullDate: null })
  }
  return result
})

function selectDate(cell) {
  if (!cell.inMonth) return
  selectedDate.value = cell.fullDate
  calDate.value = new Date(miniDate.value.getFullYear(), miniDate.value.getMonth(), cell.day)
}

function changeMonth(dir) {
  calDate.value = new Date(calDate.value.getFullYear(), calDate.value.getMonth() + dir, 1)
  miniDate.value = new Date(calDate.value)
}
function miniPrev() { miniDate.value = new Date(miniDate.value.getFullYear(), miniDate.value.getMonth() - 1, 1) }
function miniNext() { miniDate.value = new Date(miniDate.value.getFullYear(), miniDate.value.getMonth() + 1, 1) }
function goToday() {
  calDate.value = new Date()
  miniDate.value = new Date()
}

// ── 이벤트 생성 모달 ────────────────────────────────────────────────
const showCreateModal = ref(false)
const form = reactive({ title: '', description: '', start_time: '', end_time: '', is_all_day: false, color: '#3b82f6' })
const colorOptions = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#f97316', '#06b6d4', '#64748b']

function openCreate() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const dt = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`
  Object.assign(form, { title: '', description: '', start_time: dt, end_time: dt, is_all_day: false, color: '#3b82f6' })
  createError.value = ''
  showCreateModal.value = true
}

function openCreateOnDate(dateStr) {
  if (!dateStr) return
  const dt = `${dateStr}T09:00`
  Object.assign(form, { title: '', description: '', start_time: dt, end_time: `${dateStr}T10:00`, is_all_day: false, color: '#3b82f6' })
  createError.value = ''
  showCreateModal.value = true
}

async function submitCreate() {
  if (!form.title.trim()) { createError.value = '제목을 입력해 주세요.'; return }
  saving.value = true
  createError.value = ''
  try {
    const emp = authStore.user
    if (!emp?.employeeid) throw new Error('사원 정보가 없습니다. 다시 로그인해 주세요.')
    const payload = {
      employee: emp.employeeid,
      title: form.title,
      description: form.description,
      start_time: form.is_all_day ? `${form.start_time.slice(0, 10)}T00:00:00` : form.start_time + ':00',
      end_time: form.is_all_day ? `${form.start_time.slice(0, 10)}T23:59:59` : form.end_time + ':00',
      color: form.color,
      is_all_day: form.is_all_day,
    }
    await worksStore.createCalendarEvent(payload)
    showCreateModal.value = false
  } catch (e) {
    createError.value = e?.response?.data ? JSON.stringify(e.response.data) : e.message || '저장 실패'
  } finally {
    saving.value = false
  }
}

// ── 이벤트 선택/삭제 ────────────────────────────────────────────────
const selectedEv = ref(null)

function selectEvent(ev) {
  selectedEv.value = ev
}

async function deleteEvent(ev) {
  if (ev.source === 'task') return // Work관리에서 등록된 업무는 캘린더에서 직접 삭제하지 않고 업무 상세에서 처리
  if (!confirm(`"${ev.title}" 일정을 삭제하시겠습니까?`)) return
  try {
    await worksStore.deleteCalendarEvent(ev.id)
    selectedEv.value = null
  } catch {
    alert('삭제 실패')
  }
}

// ── 유틸 ────────────────────────────────────────────────────────────
function evDay(ev) { return new Date(ev.start_time || ev.start || ev.date).getDate() }
function evMonth(ev) { return `${new Date(ev.start_time || ev.start || ev.date).getMonth() + 1}월` }

function fmtTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}
function fmtDatetime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const EVENT_PALETTE = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#f97316', '#06b6d4', '#14b8a6']
function eventBgColor(ev) {
  if (ev?.color) return ev.color
  // stable color per event: use ID hash to pick from palette so overlapping events differ
  const id = ev?.id ?? 0
  const idx = typeof id === 'number' ? id : String(id).split('').reduce((h, c) => (h * 31 + c.charCodeAt(0)) & 0xffff, 0)
  return EVENT_PALETTE[idx % EVENT_PALETTE.length]
}

function eventTextColor(bg) {
  if (!bg) return '#1d4ed8'
  const hex = bg.replace('#', '')
  const r = parseInt(hex.slice(0, 2), 16)
  const g = parseInt(hex.slice(2, 4), 16)
  const b = parseInt(hex.slice(4, 6), 16)
  return (r * 0.299 + g * 0.587 + b * 0.114) > 150 ? '#1e293b' : '#fff'
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([worksStore.fetchCalendarEvents(), worksStore.fetchTasks()])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ── 레이아웃 ─────────────────────────────────────────────────────── */
.calendar-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
  min-height: calc(100vh - var(--navbar-height) - 48px);
  align-items: start;
}

.cal-left-panel {
  position: sticky;
  top: 16px;
}

/* ── 미니 캘린더 ─────────────────────────────────────────────────── */
.mini-cal { }
.mini-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}
.mini-head {
  text-align: center;
  font-size: 0.65rem;
  color: #94a3b8;
  padding: 3px 0;
  font-weight: 600;
}
.mini-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.72rem;
  color: #374151;
  transition: background 0.1s;
  position: relative;
}
.mini-cell.other-month { color: #d1d5db; cursor: default; }
.mini-cell:not(.other-month):hover { background: rgba(37,99,235,0.1); }
.mini-cell.today { background: #2563eb; color: #fff; font-weight: 700; }
.mini-cell.selected:not(.today) { background: #dbeafe; color: #1d4ed8; font-weight: 700; }
.mini-cell.has-event::after {
  content: '';
  position: absolute;
  bottom: 2px;
  width: 4px;
  height: 4px;
  background: #f59e0b;
  border-radius: 50%;
}

/* ── 캘린더 섹션 ─────────────────────────────────────────────────── */
.cal-section-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #374151;
}
.cal-check-item {
  padding: 3px 0;
}
.cal-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 2px solid;
  flex-shrink: 0;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-icon {
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px 4px;
}
.btn-icon:hover { color: #374151; }

/* ── 메인 캘린더 ─────────────────────────────────────────────────── */
.cal-header { }
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }

/* ── 월간 캘린더: 주 단위 구조 ───────────────────────────────── */
.cal-weeks-container {
  overflow: hidden;
}
.cal-header-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}
.cal-head-full {
  text-align: center;
  padding: 8px 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}
.cal-week-wrapper {
  border-bottom: 1px solid #e5e7eb;
}
.cal-week-wrapper:last-child { border-bottom: none; }

.cal-week-cells {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid #f1f5f9;
}
.cal-cell-full {
  min-height: 42px;
  padding: 5px 6px 2px;
  position: relative;
  border-right: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.1s;
}
.cal-cell-full:last-child { border-right: none; }
.cal-cell-full:hover { background: #f8fafc; }
.cal-cell-full.other-month { background: #fafafa; cursor: default; }
.cal-cell-full.other-month:hover { background: #fafafa; }
.cal-cell-full.today { background: #eff6ff; }

.cal-day-num {
  font-size: 0.8rem;
  font-weight: 600;
  color: #374151;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.cal-day-num.today-circle { background: #2563eb; color: #fff; }
.other-month .cal-day-num { color: #d1d5db; }

.cal-overflow-badge {
  font-size: 0.6rem;
  color: #64748b;
  padding: 0 2px;
}

/* 이벤트 스팬 레이어 */
.cal-event-layer {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: 22px;
  padding-bottom: 2px;
}
.cal-event-span {
  height: 20px;
  line-height: 20px;
  font-size: 0.7rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  padding: 0;
  align-self: start;
  margin-top: 1px;
  transition: opacity 0.15s;
}
.cal-event-span:hover { opacity: 0.82; }
.cal-event-span.span-start { border-radius: 4px 0 0 4px; margin-left: 3px; padding-left: 6px; }
.cal-event-span.span-end   { border-radius: 0 4px 4px 0; margin-right: 3px; }
.cal-event-span.span-start.span-end { border-radius: 4px; margin-right: 3px; }
.event-span-title {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 4px;
}

/* ── 목록 뷰 ─────────────────────────────────────────────────────── */
.event-row { cursor: pointer; transition: background 0.1s; }
.event-row:hover { background: #f8fafc; }
.event-date-badge { min-width: 36px; }
.event-color-bar { width: 3px; border-radius: 2px; flex-shrink: 0; align-self: stretch; min-height: 20px; }

/* ── 모달 ────────────────────────────────────────────────────────── */
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1300;
}
.modal-panel {
  width: 420px;
  max-height: 85vh;
  background: #fff;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-panel-header {
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
  background: #fff;
}
.btn-close-panel {
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-close-panel:hover { color: #374151; }
.modal-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.modal-panel-footer {
  padding: 12px 16px;
  border-top: 1px solid #f1f5f9;
}
.color-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: transform 0.1s;
}
.color-btn:hover { transform: scale(1.2); }
</style>
