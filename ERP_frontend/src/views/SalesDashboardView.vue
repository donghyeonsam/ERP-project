<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">영업 대시보드</h5>
        <p class="text-muted small mb-0">Sales Dashboard</p>
      </div>
      <div class="d-flex gap-2 no-print">
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
            <span :class="['badge mt-1', kpi.delta >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger']" title="전월 대비">
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
            <span class="fw-semibold small">{{ trendTitle }}</span>
          </div>
          <div class="card-body">
            <Line :data="trendChart" :options="lineOptions" style="max-height:220px" />
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
  { label: '월간', value: 'monthly' }, { label: '연간', value: 'annual' },
]

const orders = computed(() => ssafyStore.orders)
const customers = computed(() => ssafyStore.customers)
const orderDetails = computed(() => ssafyStore.orderDetails)
const products = computed(() => ssafyStore.products)

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

// 주문(Order)별 실매출 = 하위 OrderDetail의 단가*수량*(1-할인율) 합산.
// 기존엔 freight(배송비)를 "매출"로 잘못 합산하고 있었음.
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

// 연-월(YYYY-MM) 단위 집계. 데이터가 2023~2026년에 걸쳐 있어, 단순히 getMonth()로만
// 묶으면 서로 다른 해의 같은 달이 합쳐지는 오류가 있었음 — 연도까지 키에 포함해 분리.
const monthlyAgg = computed(() => {
  const map = new Map()
  orders.value.forEach((o) => {
    if (!o.orderdate) return
    const d = new Date(o.orderdate)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    if (!map.has(key)) map.set(key, { revenue: 0, orderCount: 0, customerIds: new Set() })
    const m = map.get(key)
    m.revenue += orderRevenue(o)
    m.orderCount += 1
    if (o.customerid) m.customerIds.add(o.customerid)
  })
  return map
})
const sortedMonthKeys = computed(() => [...monthlyAgg.value.keys()].sort())
const trailing12Keys = computed(() => sortedMonthKeys.value.slice(-12))

// 연간(YYYY) 단위 집계 — monthlyAgg를 연도별로 다시 묶음
const annualAgg = computed(() => {
  const map = new Map()
  monthlyAgg.value.forEach((v, key) => {
    const year = key.slice(0, 4)
    if (!map.has(year)) map.set(year, { revenue: 0, orderCount: 0, customerIds: new Set() })
    const m = map.get(year)
    m.revenue += v.revenue
    m.orderCount += v.orderCount
    v.customerIds.forEach((id) => m.customerIds.add(id))
  })
  return map
})
const sortedYearKeys = computed(() => [...annualAgg.value.keys()].sort())

const trendTitle = computed(() => (period.value === 'annual' ? '연도별 매출 추이' : '월별 매출 추이(최근 12개월)'))

const trendChart = computed(() => {
  if (period.value === 'annual') {
    return {
      labels: sortedYearKeys.value.map((y) => `${y}년`),
      datasets: [{
        label: '매출',
        data: sortedYearKeys.value.map((y) => annualAgg.value.get(y)?.revenue || 0),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37,99,235,0.1)',
        fill: true,
        tension: 0.4,
      }],
    }
  }
  return {
    labels: trailing12Keys.value.map((k) => `${k.slice(2, 4)}.${k.slice(5)}`),
    datasets: [{
      label: '매출',
      data: trailing12Keys.value.map((k) => monthlyAgg.value.get(k)?.revenue || 0),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37,99,235,0.1)',
      fill: true,
      tension: 0.4,
    }],
  }
})

// 상품(Product)의 카테고리(category_name)를 OrderDetail에 결합해 카테고리별 실매출 산출
const productCategoryMap = computed(() => new Map(products.value.map((p) => [p.productid, p.category_name || '기타'])))
const categoryRevenue = computed(() => {
  const totals = new Map()
  orderDetails.value.forEach((d) => {
    const cat = productCategoryMap.value.get(d.productid) || '기타'
    const revenue = parseFloat(d.unitprice) * d.quantity * (1 - (d.discount || 0))
    totals.set(cat, (totals.get(cat) || 0) + revenue)
  })
  return [...totals.entries()].sort((a, b) => b[1] - a[1])
})
const CATEGORY_PALETTE = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#64748b']
const categoryChart = computed(() => ({
  labels: categoryRevenue.value.map(([name]) => name),
  datasets: [{
    data: categoryRevenue.value.map(([, revenue]) => Math.round(revenue / 10000)),
    backgroundColor: categoryRevenue.value.map((_, i) => CATEGORY_PALETTE[i % CATEGORY_PALETTE.length]),
    borderWidth: 0,
  }],
}))

// shipregion(배송지역)은 대륙권 단위로 9종 고정 카테고리이며 결측치가 없어
// "지역별 매출" 집계 기준으로 사용. 매출은 OrderDetail(단가*수량*(1-할인율)) 합산으로 산출.
const REGION_LABEL = {
  'North America': '북미', 'South America': '남미', 'Central America': '중앙아메리카',
  'Western Europe': '서유럽', 'Northern Europe': '북유럽', 'Southern Europe': '남유럽',
  'Eastern Europe': '동유럽', 'Scandinavia': '스칸디나비아', 'British Isles': '영국령',
}

const regionRevenue = computed(() => {
  const totals = new Map()
  orders.value.forEach((o) => {
    const region = o.shipregion || '기타'
    totals.set(region, (totals.get(region) || 0) + orderRevenue(o))
  })
  return [...totals.entries()].sort((a, b) => b[1] - a[1])
})

const regionChart = computed(() => ({
  labels: regionRevenue.value.map(([region]) => REGION_LABEL[region] || region),
  datasets: [{
    label: '매출',
    data: regionRevenue.value.map(([, revenue]) => Math.round(revenue / 10000)),
    backgroundColor: 'rgba(37,99,235,0.7)',
  }],
}))

// 전체 주문에서 1건 이상 구매한 고객 = 활성 고객 (단순 등록 고객수와는 다름)
const activeCustomerIds = computed(() => {
  const ids = new Set()
  orders.value.forEach((o) => { if (o.customerid) ids.add(o.customerid) })
  return ids
})

function pctChange(curr, prev) {
  if (!prev) return curr > 0 ? 100 : 0
  return Math.round(((curr - prev) / prev) * 1000) / 10
}

// 배지의 증감률(delta)은 데이터상 가장 최신 달 vs 그 직전 달의 실제 변화율
const kpiCards = computed(() => {
  const keys = sortedMonthKeys.value
  const last = keys.length ? monthlyAgg.value.get(keys[keys.length - 1]) : null
  const prev = keys.length > 1 ? monthlyAgg.value.get(keys[keys.length - 2]) : null

  const totalOrders = orders.value.length
  const avgOrderValue = totalOrders ? totalRevenue.value / totalOrders : 0
  const lastAvg = last && last.orderCount ? last.revenue / last.orderCount : 0
  const prevAvg = prev && prev.orderCount ? prev.revenue / prev.orderCount : 0

  return [
    { label: '총 매출', value: `${fmtN(totalRevenue.value)}원`, icon: 'bi-cash-stack',
      delta: last && prev ? pctChange(last.revenue, prev.revenue) : 0 },
    { label: '주문 건수', value: `${totalOrders}건`, icon: 'bi-cart3',
      delta: last && prev ? pctChange(last.orderCount, prev.orderCount) : 0 },
    { label: '활성 고객수', value: `${activeCustomerIds.value.size}명`, icon: 'bi-people',
      delta: last && prev ? pctChange(last.customerIds.size, prev.customerIds.size) : 0 },
    { label: '평균 주문액', value: `${fmtN(avgOrderValue)}원`, icon: 'bi-graph-up',
      delta: prev ? pctChange(lastAvg, prevAvg) : 0 },
  ]
})

const lineOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => `${fmtN(ctx.raw)}원` } },
  },
}
const barOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => `${ctx.raw.toLocaleString('ko-KR')}만원` } },
  },
}
const donutOptions = {
  responsive: true,
  plugins: {
    legend: { position: 'bottom' },
    tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString('ko-KR')}만원` } },
  },
}

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

function printReport() {
  window.print()
}

onMounted(async () => {
  await Promise.allSettled([
    ssafyStore.fetchOrders(),
    ssafyStore.fetchCustomers(),
    ssafyStore.fetchOrderDetails(),
    ssafyStore.fetchProducts(),
  ])
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
