<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-calendar3 me-2"></i>캘린더</h5>
      <button class="btn btn-sm btn-primary" @click="showCreateModal = true">
        <i class="bi bi-plus me-1"></i>일정 추가
      </button>
    </div>

    <!-- Month navigation -->
    <div class="card erp-card mb-3">
      <div class="card-body py-2">
        <div class="d-flex align-items-center justify-content-between">
          <button class="btn btn-sm btn-outline-secondary" @click="changeMonth(-1)"><i class="bi bi-chevron-left"></i></button>
          <h6 class="mb-0 fw-bold">{{ calTitle }}</h6>
          <button class="btn btn-sm btn-outline-secondary" @click="changeMonth(1)"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="card erp-card">
      <div class="card-body p-2">
        <div class="cal-grid-full">
          <div v-for="d in dayHeaders" :key="d" class="cal-head-full">{{ d }}</div>
          <div
            v-for="cell in cells"
            :key="cell.key"
            class="cal-cell-full"
            :class="{ 'other-month': !cell.inMonth, today: cell.isToday }"
          >
            <div class="cal-day-num">{{ cell.day }}</div>
            <div
              v-for="ev in cell.events"
              :key="ev.id"
              class="cal-event"
              :title="ev.title"
            >
              {{ ev.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event list -->
    <div class="card erp-card mt-3">
      <div class="card-header py-2"><span class="fw-semibold small">이번 달 일정</span></div>
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
        <div v-else-if="monthEvents.length === 0" class="text-center text-muted small py-4">등록된 일정이 없습니다</div>
        <div v-for="ev in monthEvents" :key="ev.id" class="event-row d-flex align-items-start gap-3 p-3 border-bottom">
          <div class="event-date text-center">
            <div class="fw-bold" style="font-size:1.2rem">{{ evDay(ev) }}</div>
            <div class="text-muted small">{{ evMonth(ev) }}</div>
          </div>
          <div class="flex-grow-1">
            <div class="fw-semibold">{{ ev.title }}</div>
            <div class="text-muted small">{{ ev.description || '' }}</div>
          </div>
          <span :class="['badge align-self-start', ev.all_day ? 'bg-primary-subtle text-primary' : 'bg-info-subtle text-info']">
            {{ ev.all_day ? '종일' : '시간' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWorksStore } from '@/stores/works'

const worksStore = useWorksStore()
const loading = ref(false)
const showCreateModal = ref(false)
const calDate = ref(new Date())

const calTitle = computed(() => `${calDate.value.getFullYear()}년 ${calDate.value.getMonth()+1}월`)
const dayHeaders = ['일','월','화','수','목','금','토']

const events = computed(() => worksStore.calendarEvents)

const monthEvents = computed(() => {
  const y = calDate.value.getFullYear(), m = calDate.value.getMonth()
  return events.value.filter((e) => {
    const d = new Date(e.start || e.date)
    return d.getFullYear() === y && d.getMonth() === m
  }).sort((a, b) => new Date(a.start || a.date) - new Date(b.start || b.date))
})

const cells = computed(() => {
  const year = calDate.value.getFullYear(), month = calDate.value.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month+1, 0).getDate()
  const today = new Date()
  const evMap = {}
  monthEvents.value.forEach(ev => {
    const d = new Date(ev.start || ev.date).getDate()
    if (!evMap[d]) evMap[d] = []
    evMap[d].push(ev)
  })
  const result = []
  const prevDays = new Date(year, month, 0).getDate()
  for (let i = firstDay-1; i >= 0; i--) {
    result.push({ key: `p${i}`, day: prevDays-i, inMonth: false, isToday: false, events: [] })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear()
    result.push({ key: `c${d}`, day: d, inMonth: true, isToday, events: evMap[d] || [] })
  }
  let n = 1
  while (result.length % 7 !== 0) {
    result.push({ key: `n${n}`, day: n++, inMonth: false, isToday: false, events: [] })
  }
  return result
})

function changeMonth(dir) {
  calDate.value = new Date(calDate.value.getFullYear(), calDate.value.getMonth()+dir, 1)
}

function evDay(ev) { return new Date(ev.start || ev.date).getDate() }
function evMonth(ev) { return `${new Date(ev.start || ev.date).getMonth()+1}월` }

onMounted(async () => {
  loading.value = true
  try { await worksStore.fetchCalendarEvents() } finally { loading.value = false }
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.cal-grid-full { display: grid; grid-template-columns: repeat(7,1fr); gap: 1px; background: #f1f5f9; }
.cal-head-full { background: #f8fafc; text-align: center; padding: 6px 0; font-size: 0.75rem; font-weight: 600; color: #64748b; }
.cal-cell-full { background: #fff; min-height: 90px; padding: 4px; position: relative; }
.cal-cell-full.other-month { background: #fafafa; }
.cal-cell-full.today .cal-day-num { background: #2563eb; color: #fff; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; }
.cal-day-num { font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 2px; }
.other-month .cal-day-num { color: #d1d5db; }
.cal-event { background: #dbeafe; color: #1d4ed8; border-radius: 3px; font-size: 0.65rem; padding: 1px 4px; margin-bottom: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }
.event-row:hover { background: #f8fafc; }
.event-date { min-width: 40px; }
</style>
