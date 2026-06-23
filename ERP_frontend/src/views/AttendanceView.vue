<template>
  <div>
    <h5 class="fw-bold mb-4"><i class="bi bi-clock-history me-2"></i>근태 관리</h5>

    <!-- TODO: no backend attendance endpoint — display only shell -->
    <div class="alert alert-info small mb-4">
      <i class="bi bi-info-circle me-1"></i>
      근태 데이터 API 엔드포인트가 아직 준비되지 않았습니다.
      <!-- TODO: no backend endpoint for attendance records -->
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card erp-card text-center p-4">
          <div class="fw-bold" style="font-size:2rem">{{ currentTime }}</div>
          <div class="text-muted small mt-1">{{ todayString }}</div>
          <div class="mt-3">
            <span class="badge bg-success-subtle text-success border border-success-subtle">정상 근무</span>
          </div>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2"><span class="fw-semibold small">이번 주 근태 현황</span></div>
          <div class="card-body p-0">
            <table class="table table-sm mb-0">
              <thead class="table-light"><tr><th>날짜</th><th>출근</th><th>퇴근</th><th>근무시간</th><th>상태</th></tr></thead>
              <tbody>
                <tr v-for="row in weekRows" :key="row.date">
                  <td class="small">{{ row.date }}</td>
                  <td class="small text-muted">--:--</td>
                  <td class="small text-muted">--:--</td>
                  <td class="small text-muted">-- h</td>
                  <td><span class="badge bg-secondary-subtle text-secondary">미기록</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="card erp-card">
      <div class="card-header py-2 d-flex justify-content-between align-items-center">
        <span class="fw-semibold small">월별 근태 통계</span>
        <!-- TODO: no backend endpoint -->
      </div>
      <div class="card-body text-center text-muted py-5">
        <i class="bi bi-clock fs-1 mb-2 d-block text-muted"></i>
        백엔드 연동 후 표시됩니다
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const currentTime = ref('')
const todayString = ref('')
let timer = null

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  todayString.value = now.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
}

const weekRows = Array.from({ length: 5 }, (_, i) => {
  const d = new Date()
  const day = d.getDay()
  const diff = i - (day === 0 ? 6 : day - 1)
  const wd = new Date(d)
  wd.setDate(d.getDate() + diff)
  return { date: wd.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric', weekday: 'short' }) }
})

onMounted(() => { updateClock(); timer = setInterval(updateClock, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
