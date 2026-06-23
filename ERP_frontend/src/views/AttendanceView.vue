<template>
  <div>
    <h5 class="fw-bold mb-4"><i class="bi bi-clock-history me-2"></i>근태 내역</h5>

    <div class="row g-3 mb-4">
      <!-- 오늘 출퇴근 -->
      <div class="col-md-4">
        <div class="card erp-card text-center p-4">
          <div class="fw-bold" style="font-size:2rem">{{ currentTime }}</div>
          <div class="text-muted small mt-1">{{ todayString }}</div>
          <div class="mt-3 d-flex gap-2 justify-content-center">
            <button
              class="btn btn-sm fw-semibold"
              :class="todayRecord?.checkin_time ? 'btn-success' : 'btn-outline-success'"
              :disabled="!!todayRecord?.checkin_time || saving"
              @click="doCheckIn"
            >
              <i class="bi bi-box-arrow-in-right me-1"></i>
              {{ todayRecord?.checkin_time ? todayRecord.checkin_time.slice(0,5) : '출근' }}
            </button>
            <button
              class="btn btn-sm fw-semibold"
              :class="todayRecord?.checkout_time ? 'btn-secondary' : 'btn-outline-secondary'"
              :disabled="!todayRecord?.checkin_time || saving"
              :title="todayRecord?.checkout_time ? '클릭하여 퇴근 시간 수정' : ''"
              @click="doCheckOut"
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              {{ todayRecord?.checkout_time ? todayRecord.checkout_time.slice(0,5) + ' ✎' : '퇴근' }}
            </button>
          </div>
          <div class="mt-3">
            <span v-if="todayRecord?.checkin_time && !todayRecord?.checkout_time" class="badge bg-success-subtle text-success border border-success-subtle">근무 중</span>
            <span v-else-if="todayRecord?.checkout_time" class="badge bg-secondary-subtle text-secondary border border-secondary-subtle">퇴근 완료</span>
            <span v-else class="badge bg-warning-subtle text-warning border border-warning-subtle">미출근</span>
          </div>
        </div>
      </div>

      <!-- 이번 주 근태 현황 -->
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2 d-flex justify-content-between align-items-center">
            <span class="fw-semibold small">이번 주 근태 현황</span>
          </div>
          <div class="card-body p-0">
            <div v-if="loadingWeek" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
            <table v-else class="table table-sm mb-0">
              <thead class="table-light">
                <tr><th>날짜</th><th>출근</th><th>퇴근</th><th>근무시간</th><th>상태</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in weekRows" :key="row.date">
                  <td class="small">{{ row.label }}</td>
                  <td class="small">{{ row.record?.checkin_time?.slice(0,5) || '--:--' }}</td>
                  <td class="small">{{ row.record?.checkout_time?.slice(0,5) || '--:--' }}</td>
                  <td class="small">{{ workHours(row.record) }}</td>
                  <td>
                    <span class="badge" :class="statusBadge(row.record?.status, row.isToday)">
                      {{ row.record?.status || (row.isWeekend ? '-' : '미기록') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 월별 근태 내역 -->
    <div class="card erp-card">
      <div class="card-header py-2 d-flex justify-content-between align-items-center">
        <span class="fw-semibold small">월별 근태 내역</span>
        <div class="d-flex gap-2 align-items-center">
          <button class="btn btn-sm btn-outline-secondary px-2" @click="changeMonth(-1)"><i class="bi bi-chevron-left"></i></button>
          <span class="small fw-bold">{{ selectedMonth }}</span>
          <button class="btn btn-sm btn-outline-secondary px-2" @click="changeMonth(1)"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="loadingMonth" class="text-center py-4"><span class="spinner-border spinner-border-sm"></span></div>
        <div v-else-if="monthRecords.length === 0" class="text-center text-muted small py-5">
          <i class="bi bi-calendar-x fs-2 d-block mb-2"></i>해당 월 근태 기록이 없습니다
        </div>
        <table v-else class="table table-sm mb-0">
          <thead class="table-light">
            <tr><th>날짜</th><th>출근</th><th>퇴근</th><th>근무시간</th><th>상태</th><th>비고</th></tr>
          </thead>
          <tbody>
            <tr v-for="rec in monthRecords" :key="rec.id">
              <td class="small">{{ rec.date }}</td>
              <td class="small">{{ rec.checkin_time?.slice(0,5) || '--:--' }}</td>
              <td class="small">{{ rec.checkout_time?.slice(0,5) || '--:--' }}</td>
              <td class="small">{{ workHours(rec) }}</td>
              <td><span class="badge" :class="statusBadge(rec.status, false)">{{ rec.status || '미기록' }}</span></td>
              <td class="small text-muted">{{ rec.note || '' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { attendanceApi } from '@/api/employees'

const currentTime = ref('')
const todayString = ref('')
let timer = null

const todayRecord = ref(null)
const monthRecords = ref([])
const loadingWeek = ref(false)
const loadingMonth = ref(false)
const saving = ref(false)

const now = new Date()
const monthRef = ref({ year: now.getFullYear(), month: now.getMonth() + 1 })
const selectedMonth = computed(() => `${monthRef.value.year}년 ${monthRef.value.month}월`)

function updateClock() {
  const n = new Date()
  currentTime.value = n.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  todayString.value = n.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
}

async function loadToday() {
  try {
    const res = await attendanceApi.today()
    todayRecord.value = res.data
  } catch {
    todayRecord.value = null
  }
}

async function loadMonth() {
  loadingMonth.value = true
  try {
    const m = `${monthRef.value.year}-${String(monthRef.value.month).padStart(2, '0')}`
    const res = await attendanceApi.list(m)
    monthRecords.value = res.data
  } catch {
    monthRecords.value = []
  } finally {
    loadingMonth.value = false
  }
}

async function doCheckIn() {
  if (saving.value || todayRecord.value?.checkin_time) return
  saving.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkin(time)
    todayRecord.value = res.data
    // 월별 내역 즉시 갱신
    await loadMonth()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data || '출근 처리에 실패했습니다.'
    alert(String(msg))
  } finally {
    saving.value = false
  }
}

async function doCheckOut() {
  if (saving.value || !todayRecord.value?.checkin_time) return
  saving.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkout(time)
    todayRecord.value = res.data
    // 월별 내역 즉시 갱신
    await loadMonth()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data || '퇴근 처리에 실패했습니다.'
    alert(String(msg))
  } finally {
    saving.value = false
  }
}

function workHours(rec) {
  if (!rec?.checkin_time || !rec?.checkout_time) return '-- h'
  try {
    const [ih, im] = rec.checkin_time.split(':').map(Number)
    const [oh, om] = rec.checkout_time.split(':').map(Number)
    const diff = (oh * 60 + om) - (ih * 60 + im)
    if (diff <= 0) return '-- h'
    return `${Math.floor(diff / 60)}h ${diff % 60}m`
  } catch { return '-- h' }
}

function statusBadge(status, isToday) {
  if (!status) return isToday ? 'bg-warning-subtle text-warning' : 'bg-secondary-subtle text-secondary'
  const map = { '정상': 'bg-success-subtle text-success', '지각': 'bg-warning-subtle text-warning', '조퇴': 'bg-info-subtle text-info', '결근': 'bg-danger-subtle text-danger', '휴가': 'bg-primary-subtle text-primary' }
  return map[status] || 'bg-secondary-subtle text-secondary'
}

const weekRows = computed(() => {
  const d = new Date()
  const day = d.getDay()
  const monday = new Date(d)
  monday.setDate(d.getDate() - (day === 0 ? 6 : day - 1))

  return Array.from({ length: 7 }, (_, i) => {
    const wd = new Date(monday)
    wd.setDate(monday.getDate() + i)
    const dateStr = wd.toISOString().slice(0, 10)
    const isToday = dateStr === d.toISOString().slice(0, 10)
    const isWeekend = wd.getDay() === 0 || wd.getDay() === 6
    const record = monthRecords.value.find((r) => r.date === dateStr) ||
                   (isToday && todayRecord.value?.date === dateStr ? todayRecord.value : null)
    return {
      date: dateStr,
      label: wd.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric', weekday: 'short' }),
      isToday,
      isWeekend,
      record,
    }
  })
})

function changeMonth(dir) {
  let { year, month } = monthRef.value
  month += dir
  if (month > 12) { month = 1; year++ }
  if (month < 1) { month = 12; year-- }
  monthRef.value = { year, month }
  loadMonth()
}

onMounted(() => {
  updateClock()
  timer = setInterval(updateClock, 1000)
  loadToday()
  loadMonth()
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
