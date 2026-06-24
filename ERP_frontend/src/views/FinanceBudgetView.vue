<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-piggy-bank me-2"></i>예산관리</h5>
        <p class="text-muted small mb-0">부서별 예산 편성 및 예산 대비 실적 분석</p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">총 예산</div>
              <div class="fw-bold" style="font-size:1.4rem">{{ fmtCurrency(kpi.totalBudget) }}</div>
            </div>
            <div class="kpi-icon bg-primary-subtle text-primary"><i class="bi bi-piggy-bank"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">전체 달성률</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ kpi.achievementRate.toFixed(1) }}<span class="small fw-normal text-muted ms-1">%</span></div>
            </div>
            <div class="kpi-icon bg-success-subtle text-success"><i class="bi bi-graph-up"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">예산초과 항목</div>
              <div class="fw-bold text-warning" style="font-size:1.6rem">{{ kpi.overCount }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-warning-subtle text-warning"><i class="bi bi-exclamation-triangle"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">절감 항목</div>
              <div class="fw-bold text-info" style="font-size:1.6rem">{{ kpi.savingCount }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-info-subtle text-info"><i class="bi bi-piggy-bank"></i></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="row g-3 mb-4">
      <div class="col-md-7">
        <div class="card erp-card">
          <div class="card-header py-2 bg-white"><span class="fw-semibold small">부서별 예산 대비 실적</span></div>
          <div class="card-body">
            <Bar :data="deptChart" :options="barOptions" style="max-height:240px" />
          </div>
        </div>
      </div>
      <div class="col-md-5">
        <div class="card erp-card">
          <div class="card-header py-2 bg-white"><span class="fw-semibold small">월별 달성률 추이</span></div>
          <div class="card-body">
            <Line :data="trendChart" :options="lineOptions" style="max-height:240px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">부서</label>
            <select v-model="draft.dept" class="form-select form-select-sm">
              <option value="">전체</option>
              <option v-for="d in deptOptions" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">비용 항목</label>
            <select v-model="draft.category" class="form-select form-select-sm">
              <option value="">전체</option>
              <option v-for="c in categoryOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="draft.status" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="critical">위험초과</option>
              <option value="over">초과</option>
              <option value="normal">정상</option>
              <option value="saving">절감</option>
            </select>
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-sm btn-primary flex-grow-1" @click="applyFilters">
              <i class="bi bi-search me-1"></i>조회
            </button>
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th class="cursor-pointer" @click="toggleSort('costcenter')">부서 <i :class="sortIcon('costcenter')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('period')">기간 <i :class="sortIcon('period')"></i></th>
                <th>비용 항목</th>
                <th class="text-end cursor-pointer" @click="toggleSort('budget')">예산금액 <i :class="sortIcon('budget')"></i></th>
                <th class="text-end cursor-pointer" @click="toggleSort('actual')">실적금액 <i :class="sortIcon('actual')"></i></th>
                <th class="text-end cursor-pointer" @click="toggleSort('variance')">차이 <i :class="sortIcon('variance')"></i></th>
                <th class="text-end cursor-pointer" @click="toggleSort('achievement')">달성률 <i :class="sortIcon('achievement')"></i></th>
                <th>상태</th>
                <th>비고</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pagedRows" :key="row.id">
                <td class="small fw-semibold">{{ row.costcenter }}</td>
                <td class="small text-muted">{{ row.period }}</td>
                <td class="small">{{ row.category }}</td>
                <td class="small text-end">{{ fmtCurrency(row.budget) }}</td>
                <td class="small text-end">{{ fmtCurrency(row.actual) }}</td>
                <td class="small text-end" :class="row.variance > 0 ? 'text-danger' : 'text-success'">
                  {{ row.variance > 0 ? '+' : '' }}{{ fmtCurrency(row.variance) }}
                </td>
                <td class="small text-end fw-semibold">{{ row.achievement.toFixed(1) }}%</td>
                <td><span class="badge" :class="statusMeta(row.statusKey).cls">{{ statusMeta(row.statusKey).label }}</span></td>
                <td class="small text-muted">{{ row.remark }}</td>
              </tr>
              <tr v-if="pagedRows.length === 0">
                <td colspan="9" class="text-center text-muted small py-4">조건에 맞는 내역이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer d-flex justify-content-between align-items-center py-2 bg-white">
        <span class="small text-muted">총 {{ sortedRows.length.toLocaleString('ko-KR') }}건 중 {{ pageStartIndex + 1 }}-{{ pageEndIndex }}</span>
        <div class="d-flex gap-1 align-items-center">
          <button class="btn btn-sm btn-outline-secondary" :disabled="currentPage === 1" @click="currentPage--"><i class="bi bi-chevron-left"></i></button>
          <span class="small mx-2">{{ currentPage }} / {{ totalPages }}</span>
          <button class="btn btn-sm btn-outline-secondary" :disabled="currentPage === totalPages" @click="currentPage++"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useFinanceStore } from '@/stores/finance'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const store = useFinanceStore()

const draft = reactive({ dept: '', category: '', status: '' })
const applied = reactive({ dept: '', category: '', status: '' })

const sortKey = ref('period')
const sortDir = ref('desc')
const currentPage = ref(1)
const pageSize = 15

// ── 예산(Budget)·실적(Expense)을 기간+부서+비용항목 기준으로 매칭 ──
const rows = computed(() => {
  const expenseMap = new Map(
    store.expenses.map((e) => [`${e.period}|${e.costcenter}|${e.category}`, Number(e.amount)]),
  )
  return store.budgets.map((b) => {
    const budget = Number(b.amount)
    const actual = expenseMap.get(`${b.period}|${b.costcenter}|${b.category}`) || 0
    const achievement = budget ? (actual / budget) * 100 : 0
    const variance = actual - budget
    let statusKey = 'normal'
    if (achievement >= 115) statusKey = 'critical'
    else if (achievement >= 100) statusKey = 'over'
    else if (achievement < 90) statusKey = 'saving'
    let remark = '-'
    if (statusKey === 'critical') remark = `예산 대비 ${(achievement - 100).toFixed(0)}% 초과 (긴급 검토 필요)`
    else if (statusKey === 'over') remark = `예산 대비 ${(achievement - 100).toFixed(0)}% 초과`
    else if (statusKey === 'saving') remark = `예산 대비 ${(100 - achievement).toFixed(0)}% 절감`
    return {
      id: b.id,
      period: b.period,
      costcenter: b.costcenter,
      category: b.category,
      budget,
      actual,
      variance,
      achievement,
      statusKey,
      remark,
    }
  })
})

const deptOptions = computed(() => [...new Set(store.budgets.map((b) => b.costcenter))].sort())
const categoryOptions = computed(() => [...new Set(store.budgets.map((b) => b.category))].sort())

const kpi = computed(() => {
  const list = rows.value
  const totalBudget = list.reduce((s, r) => s + r.budget, 0)
  const totalActual = list.reduce((s, r) => s + r.actual, 0)
  return {
    totalBudget,
    achievementRate: totalBudget ? (totalActual / totalBudget) * 100 : 0,
    overCount: list.filter((r) => r.statusKey === 'over' || r.statusKey === 'critical').length,
    savingCount: list.filter((r) => r.statusKey === 'saving').length,
  }
})

const filteredRows = computed(() => {
  let list = rows.value
  if (applied.dept) list = list.filter((r) => r.costcenter === applied.dept)
  if (applied.category) list = list.filter((r) => r.category === applied.category)
  if (applied.status) list = list.filter((r) => r.statusKey === applied.status)
  return list
})

const sortedRows = computed(() => {
  const list = [...filteredRows.value]
  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  list.sort((a, b) => {
    const av = a[key]
    const bv = b[key]
    if (av === bv) return 0
    return av > bv ? dir : -dir
  })
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedRows.value.length / pageSize)))
const pageStartIndex = computed(() => (currentPage.value - 1) * pageSize)
const pageEndIndex = computed(() => Math.min(sortedRows.value.length, pageStartIndex.value + pageSize))
const pagedRows = computed(() => sortedRows.value.slice(pageStartIndex.value, pageEndIndex.value))

function applyFilters() {
  applied.dept = draft.dept
  applied.category = draft.category
  applied.status = draft.status
  currentPage.value = 1
}
function resetFilters() {
  draft.dept = ''
  draft.category = ''
  draft.status = ''
  applied.dept = ''
  applied.category = ''
  applied.status = ''
  currentPage.value = 1
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}
function sortIcon(key) {
  if (sortKey.value !== key) return 'bi bi-chevron-expand text-muted'
  return sortDir.value === 'asc' ? 'bi bi-chevron-up' : 'bi bi-chevron-down'
}

function statusMeta(key) {
  const map = {
    critical: { label: '위험초과', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    over: { label: '초과', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    normal: { label: '정상', cls: 'bg-primary-subtle text-primary border border-primary-subtle' },
    saving: { label: '절감', cls: 'bg-info-subtle text-info border border-info-subtle' },
  }
  return map[key] || { label: key, cls: 'bg-secondary-subtle text-secondary' }
}

function fmtCurrency(v) {
  if (v == null) return '-'
  const n = Number(v)
  const sign = n < 0 ? '-' : ''
  const abs = Math.abs(n)
  if (abs >= 100000000) return `${sign}${(abs / 100000000).toFixed(1)}억원`
  if (abs >= 10000) return `${sign}${(abs / 10000).toFixed(0)}만원`
  return `${sign}${Math.round(abs).toLocaleString('ko-KR')}원`
}

// ── 차트 ──
const deptChart = computed(() => {
  const depts = deptOptions.value
  const budgetByDept = depts.map((d) => rows.value.filter((r) => r.costcenter === d).reduce((s, r) => s + r.budget, 0))
  const actualByDept = depts.map((d) => rows.value.filter((r) => r.costcenter === d).reduce((s, r) => s + r.actual, 0))
  return {
    labels: depts,
    datasets: [
      { label: '예산', data: budgetByDept, backgroundColor: 'rgba(37,99,235,0.7)' },
      { label: '실적', data: actualByDept, backgroundColor: 'rgba(245,158,11,0.7)' },
    ],
  }
})

const trendChart = computed(() => {
  const periods = [...new Set(rows.value.map((r) => r.period))].sort()
  const rates = periods.map((p) => {
    const list = rows.value.filter((r) => r.period === p)
    const b = list.reduce((s, r) => s + r.budget, 0)
    const a = list.reduce((s, r) => s + r.actual, 0)
    return b ? (a / b) * 100 : 0
  })
  return {
    labels: periods,
    datasets: [{
      label: '달성률(%)',
      data: rates,
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245,158,11,0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 1,
    }],
  }
})

const barOptions = { responsive: true, plugins: { legend: { position: 'top' } } }
const lineOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { x: { ticks: { maxTicksLimit: 8 } } },
}

onMounted(() => {
  store.fetchAll()
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.kpi-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.cursor-pointer { cursor: pointer; user-select: none; }
</style>
