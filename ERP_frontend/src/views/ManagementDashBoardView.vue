<template>
  <div>
    <!-- Header -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">경영 대시보드</h5>
        <p class="text-muted small mb-0">CEO Dashboard</p>
      </div>
      <div class="d-flex gap-2 align-items-center">
        <div class="btn-group btn-group-sm">
          <button v-for="p in periods" :key="p.value" :class="['btn', period === p.value ? 'btn-primary' : 'btn-outline-secondary']" @click="period = p.value">{{ p.label }}</button>
        </div>
        <button class="btn btn-sm btn-outline-primary"><i class="bi bi-printer me-1"></i>보고서 출력</button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3" v-for="kpi in kpiCards" :key="kpi.label">
        <div class="card erp-card h-100">
          <div class="card-body">
            <div class="d-flex align-items-start justify-content-between mb-2">
              <span class="text-muted small">{{ kpi.label }}</span>
              <i :class="['bi', kpi.icon, 'text-primary']"></i>
            </div>
            <div class="fw-bold" style="font-size:1.4rem">{{ kpi.value }}</div>
            <div class="mt-1">
              <span :class="['badge', kpi.delta >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']">
                <i :class="['bi', kpi.delta >= 0 ? 'bi-arrow-up' : 'bi-arrow-down']"></i>
                {{ Math.abs(kpi.delta) }}%
              </span>
              <span class="text-muted ms-1" style="font-size:0.7rem">전월比</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="row g-3 mb-4">
      <!-- Monthly Sales & Profit -->
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2 d-flex justify-content-between align-items-center">
            <span class="fw-semibold small">월별 매출 & 영업이익 추이</span>
          </div>
          <div class="card-body">
            <Bar :data="salesChartData" :options="barOptions" style="max-height:220px" />
          </div>
        </div>
      </div>

      <!-- Channel Sales Mix (Donut) -->
      <div class="col-md-4">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">채널별 매출 비중</span>
          </div>
          <div class="card-body d-flex flex-column align-items-center">
            <Doughnut :data="channelData" :options="donutOptions" style="max-height:180px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="row g-3 mb-4">
      <!-- KPI Achievement -->
      <div class="col-md-6">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">전사 KPI 달성 현황</span>
          </div>
          <div class="card-body">
            <div v-for="item in kpiAchievement" :key="item.label" class="mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ item.label }}</span>
                <span class="fw-semibold">{{ item.value }}%</span>
              </div>
              <div class="progress" style="height:8px">
                <div class="progress-bar" :class="item.value >= 80 ? 'bg-success' : item.value >= 50 ? 'bg-warning' : 'bg-danger'" :style="`width:${item.value}%`"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Small Finance Cards + Alerts -->
      <div class="col-md-6">
        <div class="row g-2 mb-2">
          <div class="col-4">
            <div class="card erp-card text-center p-2">
              <div class="text-muted small mb-1">매출채권 잔액</div>
              <div class="fw-bold small">{{ fmt(totalReceivable) }}원</div>
            </div>
          </div>
          <div class="col-4">
            <div class="card erp-card text-center p-2">
              <div class="text-muted small mb-1">매입채무 잔액</div>
              <div class="fw-bold small">{{ fmt(totalPayable) }}원</div>
            </div>
          </div>
          <div class="col-4">
            <div class="card erp-card text-center p-2">
              <div class="text-muted small mb-1">현금성자산</div>
              <!-- TODO: no backend endpoint for cash assets -->
              <div class="fw-bold small text-muted">--</div>
            </div>
          </div>
        </div>
        <!-- Alerts feed -->
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small"><i class="bi bi-exclamation-triangle text-warning me-1"></i>긴급 알림</span>
          </div>
          <div class="card-body p-2" style="max-height:180px;overflow-y:auto">
            <div v-if="notifications.length === 0" class="text-muted small text-center py-2">알림 없음</div>
            <div v-for="n in notifications.slice(0,8)" :key="n.id" class="alert-item p-2 mb-1 rounded">
              <div class="small fw-semibold text-truncate">{{ n.title || '알림' }}</div>
              <div class="text-muted text-truncate" style="font-size:0.7rem">{{ n.message || n.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Employee count -->
    <div class="row g-3">
      <div class="col-md-4">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">임직원 수</div>
          <div class="fw-bold" style="font-size:1.8rem">{{ employees.length }}</div>
          <div class="text-muted small">명</div>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">월별 현금흐름</span>
          </div>
          <div class="card-body">
            <!-- TODO: no backend endpoint for cash flow -->
            <Line :data="cashFlowData" :options="lineOptions" style="max-height:120px" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useSsafyStore } from '@/stores/ssafy'
import { useEmployeeStore } from '@/stores/employees'
import { useFinanceStore } from '@/stores/finance'
import { useWorksStore } from '@/stores/works'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend)

const ssafyStore = useSsafyStore()
const employeeStore = useEmployeeStore()
const financeStore = useFinanceStore()
const worksStore = useWorksStore()

const period = ref('monthly')
const periods = [
  { label: '일간', value: 'daily' },
  { label: '주간', value: 'weekly' },
  { label: '월간', value: 'monthly' },
  { label: '분기', value: 'quarterly' },
  { label: '연간', value: 'annual' },
]

const orders = computed(() => ssafyStore.orders)
const employees = computed(() => employeeStore.employees)
const notifications = computed(() => worksStore.notifications)
const receivables = computed(() => financeStore.receivables)
const payables = computed(() => financeStore.payables)

const totalReceivable = computed(() =>
  receivables.value.reduce((s, r) => s + (parseFloat(r.amount) || 0), 0),
)
const totalPayable = computed(() =>
  payables.value.reduce((s, p) => s + (parseFloat(p.amount) || 0), 0),
)

const months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

function monthlySales() {
  const buckets = new Array(12).fill(0)
  orders.value.forEach((o) => {
    if (!o.orderdate) return
    const m = new Date(o.orderdate).getMonth()
    buckets[m] += parseFloat(o.freight) || 0
  })
  return buckets
}

const salesChartData = computed(() => ({
  labels: months,
  datasets: [
    {
      type: 'bar',
      label: '매출액',
      data: monthlySales(),
      backgroundColor: 'rgba(37,99,235,0.7)',
    },
    {
      type: 'line',
      label: '영업이익 (추정)',
      data: monthlySales().map((v) => v * 0.18),
      borderColor: '#f59e0b',
      backgroundColor: 'transparent',
      tension: 0.4,
    },
  ],
}))

const channelData = computed(() => ({
  labels: ['직접영업', '온라인', '대리점', '기타'],
  datasets: [{
    data: [42, 28, 20, 10],
    backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444'],
    borderWidth: 0,
  }],
}))

const cashFlowData = computed(() => ({
  labels: months,
  datasets: [{
    // TODO: no backend endpoint for cash flow
    label: '현금흐름 (placeholder)',
    data: [120, 145, 132, 160, 140, 175, 165, 180, 190, 170, 200, 210],
    borderColor: '#2563eb',
    backgroundColor: 'rgba(37,99,235,0.08)',
    fill: true,
    tension: 0.4,
  }],
}))

const kpiAchievement = [
  { label: '매출 목표 달성률', value: 82 },
  { label: '생산 가동률', value: 76 },
  { label: '납기 준수율', value: 91 },
  { label: '품질 합격률', value: 95 },
]

const kpiCards = computed(() => [
  { label: '연간 매출액', value: `${fmt(monthlySales().reduce((a,b)=>a+b,0))}원`, icon: 'bi-graph-up', delta: 12 },
  { label: '영업이익', value: `${fmt(monthlySales().reduce((a,b)=>a+b,0)*0.18)}원`, icon: 'bi-cash-stack', delta: 8 },
  { label: '영업이익률', value: '18.0%', icon: 'bi-percent', delta: 2 },
  { label: '목표 달성률', value: '82%', icon: 'bi-trophy', delta: 5 },
  { label: '생산 가동률', value: '76%', icon: 'bi-gear', delta: -3 },
  { label: '납기 준수율', value: '91%', icon: 'bi-truck', delta: 4 },
  { label: '품질 합격률', value: '95%', icon: 'bi-check-circle', delta: 1 },
  { label: '임직원 수', value: `${employees.value.length}명`, icon: 'bi-people', delta: 0 },
])

const barOptions = { responsive: true, plugins: { legend: { position: 'top' } } }
const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }
const lineOptions = { responsive: true, plugins: { legend: { display: false } } }

function fmt(n) {
  if (!n) return '0'
  if (n >= 100000000) return `${(n/100000000).toFixed(1)}억`
  if (n >= 10000) return `${(n/10000).toFixed(0)}만`
  return Math.round(n).toLocaleString()
}

onMounted(async () => {
  await Promise.allSettled([
    ssafyStore.fetchOrders(),
    employeeStore.fetchAll(),
    financeStore.fetchAll(),
    worksStore.fetchNotifications(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.alert-item { background: #fef9c3; border: 1px solid #fde68a; }
.alert-item:hover { background: #fef08a; }
</style>
