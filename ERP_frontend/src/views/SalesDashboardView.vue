<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">영업 대시보드</h5>
        <p class="text-muted small mb-0">Sales Dashboard</p>
      </div>
      <div class="d-flex gap-2">
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
            <span :class="['badge mt-1', kpi.delta >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']">
              <i :class="['bi', kpi.delta >= 0 ? 'bi-arrow-up' : 'bi-arrow-down']"></i>
              {{ Math.abs(kpi.delta) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="row g-3 mb-4">
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">월별 매출 추이</span>
          </div>
          <div class="card-body">
            <Line :data="monthlySalesChart" :options="lineOptions" style="max-height:220px" />
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">카테고리별 매출</span>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <Doughnut :data="categoryChart" :options="donutOptions" style="max-height:180px" />
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">지역별 매출</span>
          </div>
          <div class="card-body">
            <Bar :data="regionChart" :options="barOptions" style="max-height:200px" />
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">주요 고객</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm table-hover mb-0">
                <thead class="table-light">
                  <tr><th>고객명</th><th>국가</th><th>주문수</th></tr>
                </thead>
                <tbody>
                  <tr v-for="c in topCustomers" :key="c.customerid">
                    <td class="small">{{ c.companyname }}</td>
                    <td class="small text-muted">{{ c.country }}</td>
                    <td class="small fw-semibold">{{ c.orderCount }}</td>
                  </tr>
                  <tr v-if="topCustomers.length === 0">
                    <td colspan="3" class="text-center text-muted small py-3">데이터 없음</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="card erp-card">
      <div class="card-header py-2 d-flex justify-content-between align-items-center">
        <span class="fw-semibold small">최근 주문</span>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>#주문ID</th><th>고객ID</th><th>담당자</th><th>주문일</th><th>배송일</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="o in recentOrders" :key="o.orderid">
                <td class="small fw-semibold">{{ o.orderid }}</td>
                <td class="small">{{ o.customerid }}</td>
                <td class="small">{{ o.employeeid }}</td>
                <td class="small text-muted">{{ fmt(o.orderdate) }}</td>
                <td class="small text-muted">{{ fmt(o.shippeddate) }}</td>
                <td>
                  <span :class="['badge', o.shippeddate ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning']">
                    {{ o.shippeddate ? '출하완료' : '처리중' }}
                  </span>
                </td>
              </tr>
              <tr v-if="recentOrders.length === 0">
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
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useSsafyStore } from '@/stores/ssafy'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend)

const ssafyStore = useSsafyStore()
const period = ref('monthly')
const periods = [
  { label: '일간', value: 'daily' }, { label: '주간', value: 'weekly' },
  { label: '월간', value: 'monthly' }, { label: '분기', value: 'quarterly' }, { label: '연간', value: 'annual' },
]

const orders = computed(() => ssafyStore.orders)
const customers = computed(() => ssafyStore.customers)

const recentOrders = computed(() =>
  [...orders.value].sort((a, b) => new Date(b.orderdate) - new Date(a.orderdate)).slice(0, 10),
)

const topCustomers = computed(() => {
  const counts = {}
  orders.value.forEach((o) => { counts[o.customerid] = (counts[o.customerid] || 0) + 1 })
  return customers.value
    .map((c) => ({ ...c, orderCount: counts[c.customerid] || 0 }))
    .sort((a, b) => b.orderCount - a.orderCount)
    .slice(0, 8)
})

function monthlyBuckets() {
  const b = new Array(12).fill(0)
  orders.value.forEach((o) => {
    if (!o.orderdate) return
    b[new Date(o.orderdate).getMonth()] += parseFloat(o.freight) || 0
  })
  return b
}

const months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

const monthlySalesChart = computed(() => ({
  labels: months,
  datasets: [{
    label: '매출',
    data: monthlyBuckets(),
    borderColor: '#2563eb',
    backgroundColor: 'rgba(37,99,235,0.1)',
    fill: true,
    tension: 0.4,
  }],
}))

const categoryChart = computed(() => ({
  labels: ['Category 1','Category 2','Category 3','Category 4','기타'],
  datasets: [{
    data: [30, 25, 20, 15, 10],
    backgroundColor: ['#2563eb','#10b981','#f59e0b','#ef4444','#8b5cf6'],
    borderWidth: 0,
  }],
}))

const regionChart = computed(() => ({
  labels: ['Region 1','Region 2','Region 3','Region 4'],
  datasets: [{
    label: '매출',
    data: [850, 620, 740, 480],
    backgroundColor: 'rgba(37,99,235,0.7)',
  }],
}))

const kpiCards = computed(() => {
  const total = monthlyBuckets().reduce((a, b) => a + b, 0)
  return [
    { label: '총 매출', value: `${fmtN(total)}원`, icon: 'bi-cash-stack', delta: 12 },
    { label: '주문 건수', value: `${orders.value.length}건`, icon: 'bi-cart3', delta: 5 },
    { label: '활성 고객수', value: `${customers.value.length}명`, icon: 'bi-people', delta: 3 },
    { label: '평균 주문액', value: `${fmtN(orders.value.length ? total/orders.value.length : 0)}원`, icon: 'bi-graph-up', delta: -2 },
  ]
})

const lineOptions = { responsive: true, plugins: { legend: { display: false } } }
const barOptions = { responsive: true, plugins: { legend: { display: false } } }
const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }

function fmtN(n) {
  if (!n) return '0'
  if (n >= 100000000) return `${(n/100000000).toFixed(1)}억`
  if (n >= 10000) return `${(n/10000).toFixed(0)}만`
  return Math.round(n).toLocaleString()
}

function fmt(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}

onMounted(async () => {
  await Promise.allSettled([
    ssafyStore.fetchOrders(),
    ssafyStore.fetchCustomers(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
