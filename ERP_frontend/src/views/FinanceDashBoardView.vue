<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">재무/회계 대시보드</h5>
        <p class="text-muted small mb-0">Finance & Accounting Dashboard</p>
      </div>
      <div class="d-flex gap-2">
        <div class="btn-group btn-group-sm">
          <button v-for="p in periods" :key="p.value" :class="['btn', period === p.value ? 'btn-primary' : 'btn-outline-secondary']" @click="period = p.value">{{ p.label }}</button>
        </div>
        <button class="btn btn-sm btn-outline-primary"><i class="bi bi-printer me-1"></i>보고서 출력</button>
      </div>
    </div>

    <!-- KPI -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">매출액</div>
          <div class="fw-bold" style="font-size:1.4rem">{{ fmtN(totalRevenue) }}원</div>
          <span class="badge bg-success-subtle text-success mt-1">+12%</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">영업이익</div>
          <div class="fw-bold" style="font-size:1.4rem">{{ fmtN(totalRevenue * 0.18) }}원</div>
          <span class="badge bg-success-subtle text-success mt-1">+8%</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">영업이익률</div>
          <div class="fw-bold" style="font-size:1.4rem">18.0%</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <!-- TODO: no backend endpoint for cash assets -->
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">현금성자산</div>
          <div class="fw-bold text-muted" style="font-size:1.4rem">--</div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item" v-for="tab in tabs" :key="tab">
        <button :class="['nav-link', activeTab === tab ? 'active' : '']" @click="activeTab = tab">{{ tab }}</button>
      </li>
    </ul>

    <!-- 손익 tab -->
    <div v-if="activeTab === '손익'">
      <div class="row g-3">
        <div class="col-md-8">
          <div class="card erp-card">
            <div class="card-header py-2"><span class="fw-semibold small">월별 손익 현황</span></div>
            <div class="card-body">
              <Bar :data="plChart" :options="barOptions" style="max-height:240px" />
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card erp-card">
            <div class="card-header py-2"><span class="fw-semibold small">영업이익률 추이</span></div>
            <div class="card-body">
              <Line :data="profitRateChart" :options="lineOptions" style="max-height:240px" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 현금흐름 tab -->
    <div v-if="activeTab === '현금흐름'">
      <!-- TODO: no backend endpoint for cash flow -->
      <div class="card erp-card">
        <div class="card-header py-2"><span class="fw-semibold small">월별 현금흐름 (placeholder)</span></div>
        <div class="card-body">
          <Line :data="cashFlowChart" :options="lineOptions" style="max-height:260px" />
        </div>
      </div>
    </div>

    <!-- 매출채권/매입채무 tab -->
    <div v-if="activeTab === '예산집행' || activeTab === '재무상태'">
      <div class="row g-3">
        <!-- Receivables -->
        <div class="col-md-6">
          <div class="card erp-card">
            <div class="card-header py-2"><span class="fw-semibold small">매출채권 현황</span></div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr><th>ID</th><th>금액</th><th>만기일</th><th>상태</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="r in store.receivables.slice(0,8)" :key="r.id">
                      <td class="small">{{ r.id }}</td>
                      <td class="small fw-semibold">{{ fmtN(r.amount) }}원</td>
                      <td class="small text-muted">{{ fmtDate(r.due_date || r.duedate) }}</td>
                      <td><span :class="['badge', isOverdue(r) ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success']">{{ isOverdue(r) ? '연체' : '정상' }}</span></td>
                    </tr>
                    <tr v-if="store.receivables.length === 0">
                      <td colspan="4" class="text-center text-muted small py-3">데이터 없음</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Payables -->
        <div class="col-md-6">
          <div class="card erp-card">
            <div class="card-header py-2"><span class="fw-semibold small">매입채무 현황</span></div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr><th>ID</th><th>금액</th><th>만기일</th><th>상태</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="p in store.payables.slice(0,8)" :key="p.id">
                      <td class="small">{{ p.id }}</td>
                      <td class="small fw-semibold">{{ fmtN(p.amount) }}원</td>
                      <td class="small text-muted">{{ fmtDate(p.due_date || p.duedate) }}</td>
                      <td><span :class="['badge', isOverdue(p) ? 'bg-danger-subtle text-danger' : 'bg-success-subtle text-success']">{{ isOverdue(p) ? '연체' : '정상' }}</span></td>
                    </tr>
                    <tr v-if="store.payables.length === 0">
                      <td colspan="4" class="text-center text-muted small py-3">데이터 없음</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useFinanceStore } from '@/stores/finance'
import { useSsafyStore } from '@/stores/ssafy'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const store = useFinanceStore()
const ssafyStore = useSsafyStore()

const period = ref('monthly')
const periods = [
  { label: '일간', value: 'daily' }, { label: '주간', value: 'weekly' },
  { label: '월간', value: 'monthly' }, { label: '분기', value: 'quarterly' }, { label: '연간', value: 'annual' },
]
const tabs = ['손익', '현금흐름', '예산집행', '재무상태']
const activeTab = ref('손익')

const orders = computed(() => ssafyStore.orders)

const totalRevenue = computed(() =>
  orders.value.reduce((s, o) => s + (parseFloat(o.freight) || 0), 0),
)

const months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

function monthlyRevenue() {
  const b = new Array(12).fill(0)
  orders.value.forEach((o) => {
    if (!o.orderdate) return
    b[new Date(o.orderdate).getMonth()] += parseFloat(o.freight) || 0
  })
  return b
}

const plChart = computed(() => ({
  labels: months,
  datasets: [
    { label: '매출', data: monthlyRevenue(), backgroundColor: 'rgba(37,99,235,0.7)' },
    { label: '영업이익', data: monthlyRevenue().map(v => v * 0.18), backgroundColor: 'rgba(16,185,129,0.7)' },
  ],
}))

const profitRateChart = computed(() => ({
  labels: months,
  datasets: [{
    label: '영업이익률(%)',
    data: months.map(() => 15 + Math.random() * 6),
    borderColor: '#f59e0b',
    backgroundColor: 'rgba(245,158,11,0.1)',
    fill: true,
    tension: 0.4,
  }],
}))

const cashFlowChart = computed(() => ({
  labels: months,
  datasets: [{
    // TODO: no backend endpoint for cash flow
    label: '현금흐름 (placeholder)',
    data: [120,145,132,160,140,175,165,180,190,170,200,210],
    borderColor: '#2563eb',
    backgroundColor: 'rgba(37,99,235,0.08)',
    fill: true,
    tension: 0.4,
  }],
}))

const barOptions = { responsive: true, plugins: { legend: { position: 'top' } } }
const lineOptions = { responsive: true, plugins: { legend: { display: false } } }

function fmtN(n) {
  if (!n) return '0'
  if (n >= 100000000) return `${(n/100000000).toFixed(1)}억`
  if (n >= 10000) return `${(n/10000).toFixed(0)}만`
  return Math.round(n).toLocaleString()
}

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

function isOverdue(item) {
  const due = item.due_date || item.duedate
  return due && new Date(due) < new Date()
}

onMounted(async () => {
  await Promise.allSettled([
    store.fetchAll(),
    ssafyStore.fetchOrders(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
