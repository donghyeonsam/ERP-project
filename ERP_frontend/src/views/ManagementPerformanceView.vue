<template>
  <div class="perf-page">
    <!-- 페이지 헤더 -->
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-graph-up me-2 text-primary"></i>성과 분석</h5>
        <p class="text-muted small mb-0">영업사원별·채널별·제품별 판매 성과를 다각도로 분석합니다</p>
      </div>
      <button class="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1" @click="downloadExcel">
        <i class="bi bi-download"></i>
        <span>Excel 다운로드</span>
      </button>
    </div>

    <!-- KPI 카드 4개 -->
    <div class="kpi-grid mb-4">
      <div v-for="kpi in kpiCards" :key="kpi.label" class="kpi-card erp-card">
        <div class="kpi-card-body">
          <div class="kpi-icon-wrap" :class="kpi.iconBg">
            <i :class="['bi', kpi.icon]" :style="`color:${kpi.iconColor}`"></i>
          </div>
          <div class="kpi-info">
            <div class="kpi-label text-muted">{{ kpi.label }}</div>
            <div class="kpi-value">{{ kpi.value }}</div>
            <div class="kpi-trend text-muted">{{ kpi.sub }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 영업사원 성과 -->
    <div class="erp-card tab-content-card">
      <div>
        <!-- 차트 영역 -->
        <div class="chart-section">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <span class="fw-semibold small">영업사원별 달성률 (만원)</span>
            <div class="d-flex gap-2 small">
              <span class="legend-dot" style="background:#e2e8f0"></span><span class="text-muted me-2">목표</span>
              <span class="legend-dot" style="background:#3b82f6"></span><span class="text-muted">실적</span>
            </div>
          </div>
          <div class="chart-wrap">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- 데이터 테이블 -->
        <div v-if="!perfRows.length" class="text-center text-muted py-5">
          <span class="spinner-border spinner-border-sm me-2"></span>데이터를 불러오는 중입니다
        </div>
        <div v-else class="table-section">
          <table class="perf-table w-100">
            <thead>
              <tr>
                <th><input type="checkbox" @change="toggleAllRows" :checked="allSelected" /></th>
                <th @click="sortBy('name')" class="sortable">
                  성명 <i :class="sortIcon('name')" class="bi ms-1"></i>
                </th>
                <th>소속</th>
                <th @click="sortBy('target')" class="sortable">
                  목표(만원) <i :class="sortIcon('target')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('actual')" class="sortable">
                  실적(만원) <i :class="sortIcon('actual')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('rate')" class="sortable">
                  달성률(%) <i :class="sortIcon('rate')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('yoy')" class="sortable">
                  성장률(%) <i :class="sortIcon('yoy')" class="bi ms-1"></i>
                </th>
                <th>담당거래처</th>
                <th>신규확보</th>
                <th>등급</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in sortedData" :key="row.name" :class="{ selected: row.selected }">
                <td><input type="checkbox" v-model="row.selected" /></td>
                <td class="fw-semibold">{{ row.name }}</td>
                <td class="text-muted">{{ row.dept }}</td>
                <td>{{ row.target.toLocaleString() }}</td>
                <td class="fw-semibold">{{ row.actual.toLocaleString() }}</td>
                <td>
                  <span :class="rateClass(row)">{{ achievementRate(row) }}%</span>
                </td>
                <td :class="row.yoy >= 0 ? 'text-success' : 'text-danger'">
                  {{ row.yoy >= 0 ? '+' : '' }}{{ row.yoy }}%
                </td>
                <td>{{ row.customers }}</td>
                <td>{{ row.newCustomers }}</td>
                <td>
                  <span class="grade-badge" :class="`grade-${row.grade.toLowerCase()}`">{{ row.grade }}</span>
                </td>
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
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useEmployeeStore } from '@/stores/employees'
import { useSsafyStore } from '@/stores/ssafy'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const employeeStore = useEmployeeStore()
const ssafyStore = useSsafyStore()

// ── 직책 표시명 ──────────────────────────────────────────────────────
const TITLE_LABEL = {
  'Sales Representative': '영업담당',
  'Sales Manager': '영업관리자',
  'Vice President, Sales': '영업총괄',
  'Inside Sales Coordinator': '내부영업',
  '대표이사': '대표이사',
}
function deptLabel(title) {
  return TITLE_LABEL[title] || title || '-'
}

// ── 실데이터 기준 결정론적 가중치 (목표치 산출용. 실제 영업목표 데이터가 없어 실적 대비 80~120% 범위로 역산) ──
function seededRatio(seed, salt, min, max) {
  const x = Math.sin(seed * 9301 + salt * 49297) * 10000
  const r = x - Math.floor(x)
  return min + r * (max - min)
}

// ── 주문(Order) + 주문상세(Orderdetail) + 직원(Employee)을 결합해 영업사원별 실적을 산출 ──
const perfRows = computed(() => {
  const orders = ssafyStore.orders
  const details = ssafyStore.orderDetails
  const employees = employeeStore.employees
  if (!orders.length || !details.length || !employees.length) return []

  const empMap = new Map(employees.map((e) => [e.employeeid, e]))
  const orderMap = new Map(orders.map((o) => [o.orderid, o]))

  // 전체 주문기간의 중간 시점 — 이전/이후 구간을 나눠 성장률·신규확보를 판단하는 기준점
  const validDates = orders.map((o) => new Date(o.orderdate)).filter((d) => !isNaN(d))
  const minTime = Math.min(...validDates.map((d) => d.getTime()))
  const maxTime = Math.max(...validDates.map((d) => d.getTime()))
  const midTime = (minTime + maxTime) / 2

  // 고객별 최초 주문 담당자 — "이 영업사원이 처음으로 유치한 거래처 수"(신규확보)로 집계
  // (이 데이터셋은 신규 거래처 유입이 2024년에 멈춰있어, 최근 구간으로 한정하면 전원 0건이 되어버림)
  const customerFirstOrder = new Map()
  orders.forEach((o) => {
    const t = new Date(o.orderdate).getTime()
    if (isNaN(t)) return
    const existing = customerFirstOrder.get(o.customerid)
    if (!existing || t < existing.time) {
      customerFirstOrder.set(o.customerid, { time: t, employeeid: o.employeeid })
    }
  })
  const newCustomerCount = new Map()
  customerFirstOrder.forEach(({ employeeid }) => {
    if (employeeid) {
      newCustomerCount.set(employeeid, (newCustomerCount.get(employeeid) || 0) + 1)
    }
  })

  // 직원별 실적(주문상세 매출) 집계 — 기준 시점 이전/이후로 나눠 성장률 계산
  const buckets = new Map()
  details.forEach((d) => {
    const order = orderMap.get(d.orderid)
    if (!order || !order.employeeid) return
    const t = new Date(order.orderdate).getTime()
    if (!buckets.has(order.employeeid)) {
      buckets.set(order.employeeid, { before: 0, after: 0, customerIds: new Set() })
    }
    const b = buckets.get(order.employeeid)
    const lineRevenue = Number(d.unitprice) * d.quantity * (1 - (d.discount || 0))
    if (t >= midTime) b.after += lineRevenue
    else b.before += lineRevenue
    b.customerIds.add(order.customerid)
  })

  const rows = []
  buckets.forEach((b, eid) => {
    const emp = empMap.get(eid)
    if (!emp) return
    const revenue = b.before + b.after
    const achievementTarget = seededRatio(eid, 1, 0.8, 1.2)
    const target = revenue / achievementTarget
    const growth = b.before > 0 ? ((b.after - b.before) / b.before) * 100 : (b.after > 0 ? 100 : 0)
    const rate = target ? (revenue / target) * 100 : 0
    rows.push({
      employeeid: eid,
      name: `${emp.lastname}${emp.firstname}`,
      dept: deptLabel(emp.title),
      target: Math.round(target / 10000),
      actual: Math.round(revenue / 10000),
      yoy: Math.round(growth * 10) / 10,
      customers: b.customerIds.size,
      newCustomers: newCustomerCount.get(eid) || 0,
      grade: gradeFor(rate),
      selected: false,
    })
  })
  return rows
})

// perfRows의 target/actual은 "만원" 단위로 저장되어 있음
function fmtManwon(v) {
  if (!v) return '0만원'
  if (v >= 10000) return `${(v / 10000).toFixed(1)}억원`
  return `${Math.round(v).toLocaleString('ko-KR')}만원`
}

function gradeFor(rate) {
  if (rate >= 110) return 'S'
  if (rate >= 100) return 'A'
  if (rate >= 90) return 'B'
  if (rate >= 80) return 'C'
  return 'D'
}

// ── KPI 카드 ────────────────────────────────────────────────────────
const kpiCards = computed(() => {
  const rows = perfRows.value
  const totalActual = rows.reduce((s, r) => s + r.actual, 0)
  const totalTarget = rows.reduce((s, r) => s + r.target, 0)
  const overallRate = totalTarget ? (totalActual / totalTarget) * 100 : 0
  const top = rows.length ? rows.reduce((a, b) => (achievementRate(b) > achievementRate(a) ? b : a)) : null
  return [
    { label: '총 영업실적', value: fmtManwon(totalActual), icon: 'bi-graph-up-arrow', iconColor: '#3b82f6', iconBg: 'kpi-icon-blue', sub: `영업사원 ${rows.length}명 합계` },
    { label: '목표 달성률', value: `${overallRate.toFixed(1)}%`, icon: 'bi-bullseye', iconColor: '#10b981', iconBg: 'kpi-icon-green', sub: '목표 대비 실적' },
    { label: '영업사원 수', value: `${rows.length}명`, icon: 'bi-people', iconColor: '#8b5cf6', iconBg: 'kpi-icon-purple', sub: '실적 보유 인원' },
    { label: '최고 달성자', value: top ? `${achievementRate(top)}%` : '-', icon: 'bi-trophy', iconColor: '#f59e0b', iconBg: 'kpi-icon-yellow', sub: top ? top.name : '-' },
  ]
})

// ── 정렬 ────────────────────────────────────────────────────────────
const sortKey = ref('actual')
const sortDir = ref('desc')

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}
function sortIcon(key) {
  if (sortKey.value !== key) return 'bi-arrow-down-up text-muted'
  return sortDir.value === 'asc' ? 'bi-sort-up text-primary' : 'bi-sort-down text-primary'
}

const sortedData = computed(() => {
  return [...perfRows.value].sort((a, b) => {
    let va, vb
    if (sortKey.value === 'rate') {
      va = a.actual / a.target
      vb = b.actual / b.target
    } else {
      va = a[sortKey.value]
      vb = b[sortKey.value]
    }
    if (typeof va === 'string') return sortDir.value === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    return sortDir.value === 'asc' ? va - vb : vb - va
  })
})

// ── 체크박스 ─────────────────────────────────────────────────────────
const allSelected = computed(() => perfRows.value.length > 0 && perfRows.value.every(r => r.selected))
function toggleAllRows(e) {
  perfRows.value.forEach(r => { r.selected = e.target.checked })
}

// ── 유틸 ────────────────────────────────────────────────────────────
function achievementRate(row) {
  return row.target ? Number(((row.actual / row.target) * 100).toFixed(1)) : 0
}
function rateClass(row) {
  const r = row.target ? row.actual / row.target : 0
  if (r >= 1.1) return 'text-success fw-bold'
  if (r >= 0.95) return 'text-primary fw-semibold'
  if (r >= 0.8) return 'text-warning fw-semibold'
  return 'text-danger fw-bold'
}
function downloadExcel() {
  alert('Excel 다운로드 기능은 준비 중입니다.')
}

// ── 차트 ────────────────────────────────────────────────────────────
const chartData = computed(() => ({
  labels: perfRows.value.map(r => r.name),
  datasets: [
    {
      label: '목표',
      data: perfRows.value.map(r => r.target),
      backgroundColor: '#e2e8f0',
      borderRadius: 5,
      barPercentage: 0.7,
    },
    {
      label: '실적',
      data: perfRows.value.map(r => r.actual),
      backgroundColor: '#3b82f6',
      borderRadius: 5,
      barPercentage: 0.7,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        title: (ctx) => ctx[0].label,
        label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toLocaleString()}만원`,
        afterBody: (ctx) => {
          if (ctx[1]) {
            const target = ctx[0].raw
            const actual = ctx[1].raw
            const rate = target ? ((actual / target) * 100).toFixed(1) : '0.0'
            return [`달성률: ${rate}%`]
          }
          return []
        },
      },
      backgroundColor: '#1e293b',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      padding: 10,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11 } },
    },
    y: {
      grid: { color: '#f1f5f9' },
      ticks: {
        callback: v => `${v}`,
        font: { size: 11 },
      },
    },
  },
}

onMounted(() => {
  employeeStore.fetchAll()
  ssafyStore.fetchOrders()
  ssafyStore.fetchOrderDetails()
})
</script>

<style scoped>
.perf-page { }

.erp-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ── KPI 카드 ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.kpi-card { }
.kpi-card-body {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}
.kpi-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}
.kpi-icon-blue   { background: #eff6ff; }
.kpi-icon-green  { background: #f0fdf4; }
.kpi-icon-purple { background: #f5f3ff; }
.kpi-icon-yellow { background: #fffbeb; }

.kpi-label { font-size: 0.75rem; color: #64748b; margin-bottom: 2px; }
.kpi-value { font-size: 1.35rem; font-weight: 700; color: #1e293b; line-height: 1.2; }
.kpi-trend { font-size: 0.72rem; margin-top: 2px; }

.tab-content-card { }

/* ── 차트 ── */
.chart-section {
  padding: 14px 16px 10px;
  border-bottom: 1px solid #f1f5f9;
}
.chart-wrap {
  position: relative;
  height: 220px;
}
.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

/* ── 테이블 ── */
.table-section {
  max-height: 360px;
  overflow-y: auto;
  overflow-x: auto;
  padding: 0;
}
.perf-table {
  border-collapse: collapse;
  font-size: 0.82rem;
}
.perf-table th {
  background: #f8fafc;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
  user-select: none;
  position: sticky;
  top: 0;
  z-index: 1;
}
.perf-table th.sortable { cursor: pointer; }
.perf-table th.sortable:hover { background: #f1f5f9; }
.perf-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  white-space: nowrap;
}
.perf-table tr:last-child td { border-bottom: none; }
.perf-table tbody tr:hover { background: #f8fafc; }
.perf-table tr.selected td { background: #eff6ff; }

/* ── 등급 배지 ── */
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
}
.grade-s { background: #f5f3ff; color: #7c3aed; }
.grade-a { background: #eff6ff; color: #2563eb; }
.grade-b { background: #f0fdf4; color: #16a34a; }
.grade-c { background: #fff7ed; color: #ea580c; }
.grade-d { background: #fef2f2; color: #dc2626; }
</style>
