<template>
  <div>
    <!-- Header -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">경영 대시보드</h5>
        <p class="text-muted small mb-0">CEO Dashboard</p>
      </div>
      <div class="d-flex gap-2 align-items-center no-print">
        <div class="btn-group btn-group-sm">
          <button v-for="p in periods" :key="p.value" :class="['btn', period === p.value ? 'btn-primary' : 'btn-outline-secondary']" @click="period = p.value">{{ p.label }}</button>
        </div>
        <button class="btn btn-sm btn-outline-primary" @click="printReport"><i class="bi bi-printer me-1"></i>보고서 출력</button>
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
            <div class="mt-1" style="min-height:1.2rem">
              <template v-if="kpi.delta !== null">
                <span :class="['badge', kpi.delta >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']">
                  <i :class="['bi', kpi.delta >= 0 ? 'bi-arrow-up' : 'bi-arrow-down']"></i>
                  {{ Math.abs(kpi.delta) }}%
                </span>
                <span class="text-muted ms-1" style="font-size:0.7rem">전월比</span>
              </template>
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
            <span class="fw-semibold small">{{ trendTitle }}</span>
          </div>
          <div class="card-body">
            <Bar :data="salesChartData" :options="barOptions" style="max-height:220px" />
          </div>
        </div>
      </div>

      <!-- Country Sales Mix (Donut) -->
      <div class="col-md-4">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">거래국가별 매출 비중</span>
          </div>
          <div class="card-body d-flex flex-column align-items-center">
            <Doughnut :data="countryChart" :options="donutOptions" style="max-height:180px" />
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
                <div class="progress-bar" :class="item.value >= 80 ? 'bg-success' : item.value >= 50 ? 'bg-warning' : 'bg-danger'" :style="`width:${Math.min(item.value, 100)}%`"></div>
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
              <div class="small fw-semibold text-truncate">{{ n.message }}</div>
              <div class="text-muted text-truncate" style="font-size:0.7rem">{{ fmtDate(n.created_at) }}</div>
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
            <span class="fw-semibold small">부서별 예산 집행률</span>
          </div>
          <div class="card-body">
            <div v-for="cc in costCenterUtilization" :key="cc.name" class="mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ cc.name }}</span>
                <span class="fw-semibold">{{ fmt(cc.expense) }}원 / {{ fmt(cc.budget) }}원 ({{ cc.rate }}%)</span>
              </div>
              <div class="progress" style="height:8px">
                <div class="progress-bar" :class="cc.rate > 100 ? 'bg-danger' : cc.rate >= 80 ? 'bg-success' : 'bg-warning'" :style="`width:${Math.min(cc.rate, 100)}%`"></div>
              </div>
            </div>
            <div v-if="costCenterUtilization.length === 0" class="text-muted small text-center py-3">데이터 없음</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend,
} from 'chart.js'
import { useSsafyStore } from '@/stores/ssafy'
import { useEmployeeStore } from '@/stores/employees'
import { useFinanceStore } from '@/stores/finance'
import { useWorksStore } from '@/stores/works'
import { useProcurementStore } from '@/stores/procurement'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend)

const ssafyStore = useSsafyStore()
const employeeStore = useEmployeeStore()
const financeStore = useFinanceStore()
const worksStore = useWorksStore()
const procurementStore = useProcurementStore()

const period = ref('monthly')
const periods = [
  { label: '월간', value: 'monthly' },
  { label: '연간', value: 'annual' },
]

const orders = computed(() => ssafyStore.orders)
const orderDetails = computed(() => ssafyStore.orderDetails)
const employees = computed(() => employeeStore.employees)
const notifications = computed(() => worksStore.notifications)
const receivables = computed(() => financeStore.receivables)
const payables = computed(() => financeStore.payables)
const expenses = computed(() => financeStore.expenses)
const budgets = computed(() => financeStore.budgets)
const goodsReceipts = computed(() => procurementStore.goodsReceipts)

// "잔액"은 미수금/미지급금만 합산해야 함 (status가 'paid'인 건은 이미 완납되어 잔액이 아님)
const totalReceivable = computed(() =>
  receivables.value
    .filter((r) => r.status !== 'paid')
    .reduce((s, r) => s + (parseFloat(r.amount) || 0), 0),
)
const totalPayable = computed(() =>
  payables.value
    .filter((p) => p.status !== 'paid')
    .reduce((s, p) => s + (parseFloat(p.amount) || 0), 0),
)

// 주문(Order)별 실매출 = 하위 OrderDetail의 단가*수량*(1-할인율) 합산
// (기존엔 freight(배송비)를 "매출액"으로 잘못 합산하고 있었음)
const orderRevenueMap = computed(() => {
  const totals = new Map()
  orderDetails.value.forEach((d) => {
    const revenue = parseFloat(d.unitprice) * d.quantity * (1 - (d.discount || 0))
    totals.set(d.orderid, (totals.get(d.orderid) || 0) + revenue)
  })
  return totals
})
function orderRevenue(o) {
  return orderRevenueMap.value.get(o.orderid) || 0
}
const totalRevenue = computed(() => {
  let sum = 0
  orderRevenueMap.value.forEach((v) => { sum += v })
  return sum
})

// 연-월(YYYY-MM) 단위 매출 집계 (Expense/Budget의 period 포맷과 동일하게 맞춤)
const monthlyRevenue = computed(() => {
  const map = new Map()
  orders.value.forEach((o) => {
    if (!o.orderdate) return
    const d = new Date(o.orderdate)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    map.set(key, (map.get(key) || 0) + orderRevenue(o))
  })
  return map
})
const monthlyExpense = computed(() => {
  const map = new Map()
  expenses.value.forEach((e) => {
    map.set(e.period, (map.get(e.period) || 0) + (parseFloat(e.amount) || 0))
  })
  return map
})
// 매입채무(AccountsPayable)는 PurchaseOrder 1건당 1건씩 생성되어 매출원가(COGS)의 실데이터 근거가 됨.
// "잔액" 카드와는 달리 여기선 상태(paid 여부)와 무관하게 전부 합산 — 이미 발생한 매입원가이기 때문.
const monthlyCOGS = computed(() => {
  const map = new Map()
  payables.value.forEach((p) => {
    if (!p.invoicedate) return
    const d = new Date(p.invoicedate)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    map.set(key, (map.get(key) || 0) + (parseFloat(p.amount) || 0))
  })
  return map
})
const totalCOGS = computed(() => {
  let sum = 0
  payables.value.forEach((p) => { sum += parseFloat(p.amount) || 0 })
  return sum
})
const sortedMonthKeys = computed(() => [...monthlyRevenue.value.keys()].sort())
const trailing12Keys = computed(() => sortedMonthKeys.value.slice(-12))

// 연-월(YYYY-MM) 합계 맵을 연도(YYYY) 단위로 다시 묶음 — "연간" 토글용
function toAnnual(monthlyMap) {
  const map = new Map()
  monthlyMap.forEach((v, key) => {
    const year = key.slice(0, 4)
    map.set(year, (map.get(year) || 0) + v)
  })
  return map
}
const annualRevenue = computed(() => toAnnual(monthlyRevenue.value))
const annualCOGS = computed(() => toAnnual(monthlyCOGS.value))
const annualExpense = computed(() => toAnnual(monthlyExpense.value))
const sortedYearKeys = computed(() => [...annualRevenue.value.keys()].sort())

// 실제 매입원가(COGS) + 운영경비(Expense) 총액 — "영업이익(매출*추정 18%)" 같은 가짜 마진 대신 실데이터로 계산
const totalExpense = computed(() => {
  let sum = 0
  expenses.value.forEach((e) => { sum += parseFloat(e.amount) || 0 })
  return sum
})
const totalBudget = computed(() => {
  let sum = 0
  budgets.value.forEach((b) => { sum += parseFloat(b.amount) || 0 })
  return sum
})
const totalProfit = computed(() => totalRevenue.value - totalCOGS.value - totalExpense.value)
const profitMargin = computed(() => (totalRevenue.value ? (totalProfit.value / totalRevenue.value) * 100 : 0))
const budgetUtilization = computed(() => (totalBudget.value ? (totalExpense.value / totalBudget.value) * 100 : 0))

// 납기 준수율 = 배송완료 주문 중 요청일(requireddate) 이내 발송된 비율
const onTimeDeliveryRate = computed(() => {
  const shipped = orders.value.filter((o) => o.shippeddate && o.requireddate)
  if (!shipped.length) return 0
  const onTime = shipped.filter((o) => new Date(o.shippeddate) <= new Date(o.requireddate)).length
  return Math.round((onTime / shipped.length) * 1000) / 10
})

// 품질 합격률 = 입고 검수(GoodsReceipt) 중 qcstatus가 'pass'인 비율
const qcPassRate = computed(() => {
  if (!goodsReceipts.value.length) return 0
  const pass = goodsReceipts.value.filter((g) => g.qcstatus === 'pass').length
  return Math.round((pass / goodsReceipts.value.length) * 1000) / 10
})

function pctChange(curr, prev) {
  if (!prev) return curr > 0 ? 100 : 0
  return Math.round(((curr - prev) / prev) * 1000) / 10
}

const trendTitle = computed(() => (period.value === 'annual' ? '연도별 매출 & 영업이익 추이' : '월별 매출 & 영업이익 추이(최근 12개월)'))

const salesChartData = computed(() => {
  if (period.value === 'annual') {
    return {
      labels: sortedYearKeys.value.map((y) => `${y}년`),
      datasets: [
        {
          type: 'bar',
          label: '매출액',
          data: sortedYearKeys.value.map((y) => annualRevenue.value.get(y) || 0),
          backgroundColor: 'rgba(37,99,235,0.7)',
        },
        {
          type: 'line',
          label: '영업이익 (매출-매입원가-경비)',
          data: sortedYearKeys.value.map((y) =>
            (annualRevenue.value.get(y) || 0) - (annualCOGS.value.get(y) || 0) - (annualExpense.value.get(y) || 0)),
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          tension: 0.4,
        },
      ],
    }
  }
  return {
    labels: trailing12Keys.value.map((k) => `${k.slice(2, 4)}.${k.slice(5)}`),
    datasets: [
      {
        type: 'bar',
        label: '매출액',
        data: trailing12Keys.value.map((k) => monthlyRevenue.value.get(k) || 0),
        backgroundColor: 'rgba(37,99,235,0.7)',
      },
      {
        type: 'line',
        label: '영업이익 (매출-매입원가-경비)',
        data: trailing12Keys.value.map((k) =>
          (monthlyRevenue.value.get(k) || 0) - (monthlyCOGS.value.get(k) || 0) - (monthlyExpense.value.get(k) || 0)),
        borderColor: '#f59e0b',
        backgroundColor: 'transparent',
        tension: 0.4,
      },
    ],
  }
})

// 채널(channel) 구분 필드는 데이터에 없어 대신 거래국가(shipcountry)별 매출 비중으로 대체
const COUNTRY_PALETTE = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
const countryChart = computed(() => {
  const totals = new Map()
  orders.value.forEach((o) => {
    const country = o.shipcountry || '기타'
    totals.set(country, (totals.get(country) || 0) + orderRevenue(o))
  })
  const sorted = [...totals.entries()].sort((a, b) => b[1] - a[1])
  const top = sorted.slice(0, 4)
  const restSum = sorted.slice(4).reduce((s, [, v]) => s + v, 0)
  if (restSum > 0) top.push(['기타', restSum])
  return {
    labels: top.map(([name]) => name),
    datasets: [{
      data: top.map(([, v]) => Math.round(v / 10000)),
      backgroundColor: top.map((_, i) => COUNTRY_PALETTE[i % COUNTRY_PALETTE.length]),
      borderWidth: 0,
    }],
  }
})

// 부서(costcenter)별 예산 집행률 = 실제 경비 / 편성 예산
const costCenterUtilization = computed(() => {
  const budgetMap = new Map()
  budgets.value.forEach((b) => budgetMap.set(b.costcenter, (budgetMap.get(b.costcenter) || 0) + (parseFloat(b.amount) || 0)))
  const expenseMap = new Map()
  expenses.value.forEach((e) => expenseMap.set(e.costcenter, (expenseMap.get(e.costcenter) || 0) + (parseFloat(e.amount) || 0)))
  return [...budgetMap.entries()].map(([name, budget]) => {
    const expense = expenseMap.get(name) || 0
    return { name, budget, expense, rate: budget ? Math.round((expense / budget) * 1000) / 10 : 0 }
  }).sort((a, b) => b.budget - a.budget)
})

// 전사 KPI 달성 현황 — 전부 실데이터 기반 (생산 가동률은 이 회사에 제조 공정이 없어 제외)
const kpiAchievement = computed(() => [
  { label: '영업이익률', value: Math.round(profitMargin.value * 10) / 10 },
  { label: '예산 집행률', value: Math.round(budgetUtilization.value * 10) / 10 },
  { label: '납기 준수율', value: onTimeDeliveryRate.value },
  { label: '품질 합격률', value: qcPassRate.value },
])

// 증감률(delta)은 데이터상 최신월 vs 직전월의 실제 변화율 — 계산이 의미있는 매출/이익에만 표시
const kpiCards = computed(() => {
  const keys = sortedMonthKeys.value
  const lastKey = keys[keys.length - 1]
  const prevKey = keys[keys.length - 2]
  const lastRevenue = lastKey ? (monthlyRevenue.value.get(lastKey) || 0) : 0
  const prevRevenue = prevKey ? (monthlyRevenue.value.get(prevKey) || 0) : 0
  const lastProfit = lastKey ? lastRevenue - (monthlyCOGS.value.get(lastKey) || 0) - (monthlyExpense.value.get(lastKey) || 0) : 0
  const prevProfit = prevKey ? prevRevenue - (monthlyCOGS.value.get(prevKey) || 0) - (monthlyExpense.value.get(prevKey) || 0) : 0

  return [
    { label: '총 매출액', value: `${fmt(totalRevenue.value)}원`, icon: 'bi-graph-up',
      delta: prevKey ? pctChange(lastRevenue, prevRevenue) : null },
    { label: '영업이익', value: `${fmt(totalProfit.value)}원`, icon: 'bi-cash-stack',
      delta: prevKey ? pctChange(lastProfit, prevProfit) : null },
    { label: '영업이익률', value: `${profitMargin.value.toFixed(1)}%`, icon: 'bi-percent', delta: null },
    { label: '예산 집행률', value: `${budgetUtilization.value.toFixed(1)}%`, icon: 'bi-clipboard-check', delta: null },
    { label: '납기 준수율', value: `${onTimeDeliveryRate.value}%`, icon: 'bi-truck', delta: null },
    { label: '품질 합격률', value: `${qcPassRate.value}%`, icon: 'bi-check-circle', delta: null },
    { label: '임직원 수', value: `${employees.value.length}명`, icon: 'bi-people', delta: null },
  ]
})

const barOptions = { responsive: true, plugins: { legend: { position: 'top' } } }
const donutOptions = {
  responsive: true,
  plugins: {
    legend: { position: 'bottom' },
    tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString('ko-KR')}만원` } },
  },
}

function fmt(n) {
  if (!n) return '0'
  if (n >= 100000000) return `${(n/100000000).toFixed(1)}억`
  if (n >= 10000) return `${(n/10000).toFixed(0)}만`
  return Math.round(n).toLocaleString()
}
function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function printReport() {
  window.print()
}

onMounted(async () => {
  await Promise.allSettled([
    ssafyStore.fetchOrders(),
    ssafyStore.fetchOrderDetails(),
    employeeStore.fetchAll(),
    financeStore.fetchAll(),
    worksStore.fetchNotifications(),
    procurementStore.fetchAll(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.alert-item { background: #fef9c3; border: 1px solid #fde68a; }
.alert-item:hover { background: #fef08a; }
</style>
