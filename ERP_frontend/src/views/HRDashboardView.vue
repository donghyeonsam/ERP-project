<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">인사 대시보드</h5>
        <p class="text-muted small mb-0">HR Dashboard</p>
      </div>
      <button class="btn btn-sm btn-outline-primary"><i class="bi bi-printer me-1"></i>보고서 출력</button>
    </div>

    <!-- KPI -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">총 임직원</div>
          <div class="fw-bold" style="font-size:1.8rem">{{ store.employees.length }}</div>
          <div class="text-muted small">명</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">직급 수</div>
          <div class="fw-bold" style="font-size:1.8rem">{{ uniqueTitles.length }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <!-- TODO: no backend endpoint for payroll data -->
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">급여 총액</div>
          <div class="fw-bold text-muted" style="font-size:1.8rem">--</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <!-- TODO: no backend endpoint for attendance rate -->
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">출근율</div>
          <div class="fw-bold text-muted" style="font-size:1.8rem">--</div>
        </div>
      </div>
    </div>

    <!-- Charts + Org chart placeholder -->
    <div class="row g-3 mb-4">
      <div class="col-md-5">
        <div class="card erp-card">
          <div class="card-header py-2"><span class="fw-semibold small">직급별 인원 분포</span></div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <Doughnut :data="titleChart" :options="donutOptions" style="max-height:200px" />
          </div>
        </div>
      </div>
      <div class="col-md-7">
        <div class="card erp-card">
          <div class="card-header py-2"><span class="fw-semibold small">조직도 (org-chart)</span></div>
          <div class="card-body p-2" style="max-height:220px;overflow-y:auto">
            <div v-if="orgLoading" class="text-center py-3"><span class="spinner-border spinner-border-sm"></span></div>
            <div v-else>
              <div v-for="emp in topManagers" :key="emp.employeeid" class="org-node mb-2">
                <div class="d-flex align-items-center gap-2">
                  <div class="org-avatar">{{ initial(emp) }}</div>
                  <div>
                    <div class="small fw-semibold">{{ emp.lastname }}{{ emp.firstname }}</div>
                    <div class="text-muted" style="font-size:0.7rem">{{ emp.title }}</div>
                  </div>
                </div>
                <div class="ms-4 mt-1">
                  <div v-for="sub in directReports(emp.employeeid)" :key="sub.employeeid" class="d-flex align-items-center gap-2 mb-1">
                    <div class="org-avatar org-avatar-sm">{{ initial(sub) }}</div>
                    <div>
                      <div style="font-size:0.78rem;font-weight:600">{{ sub.lastname }}{{ sub.firstname }}</div>
                      <div class="text-muted" style="font-size:0.68rem">{{ sub.title }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Employee Table -->
    <div class="card erp-card">
      <div class="card-header py-2 d-flex justify-content-between align-items-center">
        <span class="fw-semibold small">임직원 목록</span>
        <input v-model="search" type="text" class="form-control form-control-sm w-auto" placeholder="검색..." style="max-width:180px" />
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>사원번호</th><th>이름</th><th>직급</th><th>도시</th><th>국가</th><th>입사일</th></tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.employeeid">
                <td class="small text-muted">{{ emp.employeeid }}</td>
                <td class="small fw-semibold">{{ emp.lastname }}{{ emp.firstname }}</td>
                <td class="small">{{ emp.title }}</td>
                <td class="small text-muted">{{ emp.city }}</td>
                <td class="small text-muted">{{ emp.country }}</td>
                <td class="small text-muted">{{ fmtDate(emp.hiredate) }}</td>
              </tr>
              <tr v-if="filteredEmployees.length === 0">
                <td colspan="6" class="text-center text-muted small py-3">데이터 없음</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { useEmployeeStore } from '@/stores/employees'

ChartJS.register(ArcElement, Tooltip, Legend)

const store = useEmployeeStore()
const orgLoading = ref(false)
const search = ref('')

const uniqueTitles = computed(() => [...new Set(store.employees.map(e => e.title).filter(Boolean))])

const topManagers = computed(() =>
  store.employees.filter(e => !e.reportsto || e.role_level >= 3).slice(0, 3),
)

function directReports(managerId) {
  return store.employees.filter(e => e.reportsto === managerId)
}

const filteredEmployees = computed(() => {
  if (!search.value) return store.employees
  const q = search.value.toLowerCase()
  return store.employees.filter(e =>
    `${e.lastname}${e.firstname}`.includes(q) || (e.title || '').toLowerCase().includes(q),
  )
})

const titleChart = computed(() => {
  const counts = {}
  store.employees.forEach(e => {
    const t = e.title || '기타'
    counts[t] = (counts[t] || 0) + 1
  })
  return {
    labels: Object.keys(counts),
    datasets: [{
      data: Object.values(counts),
      backgroundColor: ['#2563eb','#10b981','#f59e0b','#ef4444','#8b5cf6'],
      borderWidth: 0,
    }],
  }
})

const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }

function initial(emp) { return `${emp.lastname || ''}`.charAt(0) || 'E' }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

onMounted(async () => {
  orgLoading.value = true
  try { await store.fetchAll() } finally { orgLoading.value = false }
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.org-avatar {
  width: 32px; height: 32px; background: #2563eb; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
}
.org-avatar-sm { width: 24px; height: 24px; font-size: 0.7rem; }
.org-node { border-left: 2px solid #e5e7eb; padding-left: 8px; }
</style>
