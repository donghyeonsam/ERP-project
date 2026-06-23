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
            <div class="kpi-trend" :class="kpi.trend >= 0 ? 'text-success' : 'text-danger'">
              <i :class="kpi.trend >= 0 ? 'bi-arrow-up-right' : 'bi-arrow-down-right'" class="bi me-1"></i>
              {{ kpi.trend >= 0 ? '+' : '' }}{{ kpi.trend }}% 전년 대비
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="tab-nav mb-0">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <!-- 탭 컨텐츠 -->
    <div class="erp-card tab-content-card">
      <!-- 영업사원 성과 탭 -->
      <div v-if="activeTab === 'sales'">
        <!-- 차트 영역 -->
        <div class="chart-section">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <span class="fw-semibold small">영업사원별 달성률 (백만원)</span>
            <div class="d-flex gap-2 small">
              <span class="legend-dot" style="background:#e2e8f0"></span><span class="text-muted me-2">목표</span>
              <span class="legend-dot" style="background:#3b82f6"></span><span class="text-muted">실적</span>
            </div>
          </div>
          <Bar :data="chartData" :options="chartOptions" style="height:180px" />
        </div>

        <!-- 데이터 테이블 -->
        <div class="table-section">
          <table class="perf-table w-100">
            <thead>
              <tr>
                <th><input type="checkbox" @change="toggleAllRows" :checked="allSelected" /></th>
                <th @click="sortBy('name')" class="sortable">
                  성명 <i :class="sortIcon('name')" class="bi ms-1"></i>
                </th>
                <th>소속</th>
                <th @click="sortBy('target')" class="sortable">
                  목표(백만) <i :class="sortIcon('target')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('actual')" class="sortable">
                  실적(백만) <i :class="sortIcon('actual')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('rate')" class="sortable">
                  달성률(%) <i :class="sortIcon('rate')" class="bi ms-1"></i>
                </th>
                <th @click="sortBy('yoy')" class="sortable">
                  YOY(%) <i :class="sortIcon('yoy')" class="bi ms-1"></i>
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

      <!-- 나머지 탭: 준비 중 -->
      <div v-else class="text-center text-muted py-5">
        <i class="bi bi-bar-chart-line fs-2 d-block mb-2"></i>
        <div>{{ tabs.find(t => t.key === activeTab)?.label }} 준비 중입니다</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

// ── KPI 카드 ────────────────────────────────────────────────────────
const kpiCards = [
  { label: '총 영업실적', value: '100.4B원', trend: 12.4, icon: 'bi-graph-up-arrow', iconColor: '#3b82f6', iconBg: 'kpi-icon-blue' },
  { label: '목표 달성률', value: '105.7%',   trend: 5.2,  icon: 'bi-bullseye',       iconColor: '#10b981', iconBg: 'kpi-icon-green' },
  { label: '영업사원 수', value: '8명',       trend: 0,    icon: 'bi-people',         iconColor: '#8b5cf6', iconBg: 'kpi-icon-purple' },
  { label: '최고 달성자', value: '118.7%',   trend: 8.5,  icon: 'bi-trophy',         iconColor: '#f59e0b', iconBg: 'kpi-icon-yellow' },
]

// ── 탭 ──────────────────────────────────────────────────────────────
const tabs = [
  { key: 'sales',    label: '영업사원 성과' },
  { key: 'trend',    label: '매출 추이' },
  { key: 'channel',  label: '채널 분석' },
  { key: 'product',  label: '제품 성과' },
]
const activeTab = ref('sales')

// ── 테이블 데이터 ────────────────────────────────────────────────────
const tableData = ref([
  { name: '김영업', dept: '영업1팀', target: 1500, actual: 1780, yoy: 22.4, customers: 28, newCustomers: 5, grade: 'S', selected: false },
  { name: '이영업', dept: '영업1팀', target: 1200, actual: 1350, yoy: 15.3, customers: 22, newCustomers: 3, grade: 'A', selected: false },
  { name: '박영업', dept: '영업2팀', target: 1400, actual: 1380, yoy: 8.2,  customers: 31, newCustomers: 2, grade: 'B', selected: false },
  { name: '최영업', dept: '영업2팀', target: 1100, actual: 920,  yoy: -5.8, customers: 18, newCustomers: 1, grade: 'C', selected: false },
  { name: '정영업', dept: '영업1팀', target: 1300, actual: 1420, yoy: 12.8, customers: 25, newCustomers: 4, grade: 'A', selected: false },
  { name: '한영업', dept: '영업3팀', target: 900,  actual: 580,  yoy: -8.5, customers: 15, newCustomers: 0, grade: 'D', selected: false },
  { name: '조영업', dept: '영업3팀', target: 1050, actual: 1050, yoy: 3.2,  customers: 20, newCustomers: 2, grade: 'B', selected: false },
  { name: '윤영업', dept: '영업2팀', target: 1150, actual: 1100, yoy: 5.1,  customers: 19, newCustomers: 1, grade: 'B', selected: false },
])

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
  return [...tableData.value].sort((a, b) => {
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
const allSelected = computed(() => tableData.value.every(r => r.selected))
function toggleAllRows(e) {
  tableData.value.forEach(r => { r.selected = e.target.checked })
}

// ── 유틸 ────────────────────────────────────────────────────────────
function achievementRate(row) {
  return ((row.actual / row.target) * 100).toFixed(1)
}
function rateClass(row) {
  const r = row.actual / row.target
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
  labels: tableData.value.map(r => r.name),
  datasets: [
    {
      label: '목표',
      data: tableData.value.map(r => r.target),
      backgroundColor: '#e2e8f0',
      borderRadius: 5,
      barPercentage: 0.7,
    },
    {
      label: '실적',
      data: tableData.value.map(r => r.actual),
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
        label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toLocaleString()}백만원`,
        afterBody: (ctx) => {
          if (ctx[1]) {
            const target = ctx[0].raw
            const actual = ctx[1].raw
            const rate = ((actual / target) * 100).toFixed(1)
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

/* ── 탭 ── */
.tab-nav {
  display: flex;
  border-bottom: 2px solid #e5e7eb;
  gap: 0;
}
.tab-btn {
  border: none;
  background: transparent;
  padding: 10px 20px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s, border-color 0.15s;
}
.tab-btn:hover { color: #2563eb; }
.tab-btn.active { color: #2563eb; border-bottom-color: #2563eb; font-weight: 600; }

.tab-content-card {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  border-top: none;
}

/* ── 차트 ── */
.chart-section {
  padding: 14px 16px 10px;
  border-bottom: 1px solid #f1f5f9;
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
