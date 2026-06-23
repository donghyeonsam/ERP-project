<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">생산·물류 대시보드</h5>
        <p class="text-muted small mb-0">Production & Logistics Dashboard</p>
      </div>
      <button class="btn btn-sm btn-outline-primary"><i class="bi bi-printer me-1"></i>보고서 출력</button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <!-- TODO: no backend endpoint for production rate -->
          <div class="text-muted small mb-1">평균 생산 가동률</div>
          <div class="fw-bold text-primary" style="font-size:1.6rem">76%</div>
          <span class="badge bg-success-subtle text-success mt-1">+2% 전월比</span>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">납기 준수율</div>
          <div class="fw-bold text-success" style="font-size:1.6rem">{{ deliveryRate }}%</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <!-- TODO: no backend endpoint for quality pass rate -->
          <div class="text-muted small mb-1">품질 합격률</div>
          <div class="fw-bold text-info" style="font-size:1.6rem">95%</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">재고 이상 항목</div>
          <div class="fw-bold text-danger" style="font-size:1.6rem">{{ shortageCount }}</div>
        </div>
      </div>
    </div>

    <!-- Line status + Daily production -->
    <div class="row g-3 mb-4">
      <!-- Production line status -->
      <div class="col-md-4">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">생산라인 가동률 현황</span>
          </div>
          <div class="card-body">
            <!-- TODO: no backend endpoint for production line data -->
            <div v-for="line in productionLines" :key="line.name" class="mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ line.name }}</span>
                <span class="fw-semibold" :class="line.rate >= 80 ? 'text-success' : 'text-warning'">{{ line.rate }}%</span>
              </div>
              <div class="progress" style="height:10px">
                <div class="progress-bar" :class="line.rate >= 80 ? 'bg-success' : 'bg-warning'" :style="`width:${line.rate}%`"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Daily production chart -->
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-header py-2 d-flex align-items-center gap-2">
            <span class="fw-semibold small">일별 생산 실적</span>
            <div class="btn-group btn-group-sm ms-auto">
              <button v-for="tab in lineTabs" :key="tab" :class="['btn', activeLineTab === tab ? 'btn-primary' : 'btn-outline-secondary']" @click="activeLineTab = tab" style="font-size:0.7rem;padding:2px 8px">{{ tab }}</button>
            </div>
          </div>
          <div class="card-body">
            <!-- TODO: no backend endpoint for daily production data -->
            <Line :data="productionChartData" :options="lineOptions" style="max-height:200px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Inventory + Delivery status -->
    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">재고 현황 (적정 대비 %)</span>
          </div>
          <div class="card-body">
            <Bar :data="inventoryChart" :options="barOptions" style="max-height:200px" />
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">납기 현황</span>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <Doughnut :data="deliveryDonut" :options="donutOptions" style="max-height:180px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Shipment table -->
    <div class="card erp-card">
      <div class="card-header py-2">
        <span class="fw-semibold small">출하 예정 현황</span>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>주문ID</th><th>고객</th><th>주문일</th><th>출하예정</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="o in pendingShipments.slice(0,10)" :key="o.orderid">
                <td class="small fw-semibold">{{ o.orderid }}</td>
                <td class="small">{{ o.customerid }}</td>
                <td class="small text-muted">{{ fmtDate(o.orderdate) }}</td>
                <td class="small">{{ fmtDate(o.requireddate) }}</td>
                <td>
                  <span :class="['badge', isLate(o) ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary']">
                    {{ isLate(o) ? '지연' : '정상' }}
                  </span>
                </td>
              </tr>
              <tr v-if="pendingShipments.length === 0">
                <td colspan="5" class="text-center text-muted small py-3">데이터 없음</td>
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
import { useProcurementStore } from '@/stores/procurement'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend)

const ssafyStore = useSsafyStore()
const procStore = useProcurementStore()

const activeLineTab = ref('전체')
const lineTabs = ['전체', '1호', '2호', '3호']

// TODO: no backend endpoint for production line data
const productionLines = [
  { name: '1호 라인', rate: 82 },
  { name: '2호 라인', rate: 71 },
  { name: '3호 라인', rate: 76 },
]

const orders = computed(() => ssafyStore.orders)
const materials = computed(() => procStore.materials)

const pendingShipments = computed(() =>
  orders.value.filter((o) => !o.shippeddate)
    .sort((a, b) => new Date(a.requireddate) - new Date(b.requireddate)),
)

const deliveryRate = computed(() => {
  if (!orders.value.length) return 0
  const onTime = orders.value.filter((o) => {
    if (!o.shippeddate || !o.requireddate) return false
    return new Date(o.shippeddate) <= new Date(o.requireddate)
  }).length
  return Math.round((onTime / orders.value.length) * 100)
})

const shortageCount = computed(() => materials.value.filter((m) => (m.quantity || 0) < 10).length)

const days = Array.from({ length: 14 }, (_, i) => {
  const d = new Date()
  d.setDate(d.getDate() - 13 + i)
  return `${d.getMonth()+1}/${d.getDate()}`
})

const productionChartData = computed(() => ({
  labels: days,
  datasets: [
    { label: '계획', data: days.map(() => 100), borderColor: '#94a3b8', borderDash: [4,4], tension: 0.4, fill: false },
    // TODO: no backend endpoint for daily production
    { label: '실적', data: days.map(() => Math.round(65 + Math.random() * 30)), borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.1)', fill: true, tension: 0.4 },
  ],
}))

const inventoryChart = computed(() => ({
  labels: materials.value.slice(0, 8).map((m) => m.materialid || m.name || `M${m.id}`),
  datasets: [{
    label: '재고 비율(%)',
    data: materials.value.slice(0, 8).map(() => Math.round(40 + Math.random() * 60)),
    backgroundColor: 'rgba(37,99,235,0.7)',
  }],
}))

const deliveryDonut = computed(() => {
  const total = orders.value.length || 3
  const shipped = orders.value.filter((o) => o.shippeddate).length || 1
  const late = Math.max(0, total - shipped - 1)
  return {
    labels: ['정상', '지연', '취소'],
    datasets: [{
      data: [shipped, late, 0],
      backgroundColor: ['#10b981', '#ef4444', '#94a3b8'],
      borderWidth: 0,
    }],
  }
})

const lineOptions = { responsive: true, plugins: { legend: { position: 'top' } } }
const barOptions = { responsive: true, plugins: { legend: { display: false } } }
const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }
function isLate(o) {
  if (o.shippeddate) return false
  return o.requireddate && new Date(o.requireddate) < new Date()
}

onMounted(async () => {
  await Promise.allSettled([
    ssafyStore.fetchOrders(),
    procStore.fetchAll(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
