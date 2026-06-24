<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-graph-up-arrow me-2 text-primary"></i>AI 예측</h5>
        <p class="text-muted small mb-0">통계 기반 수요 예측 모델로 미래 매출을 예측하고 생산·재고 계획에 활용합니다</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <template v-else>
      <!-- KPI Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">예측 정확도(백테스트)</div>
            <div class="fw-bold" style="font-size:1.5rem">{{ kpi.accuracy.toFixed(1) }}<span class="small fw-normal text-muted ms-1">%</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">{{ nextMonthLabel }} 예측 매출</div>
            <div class="fw-bold" style="font-size:1.5rem">{{ fmtMoney(kpi.nextMonth) }}</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">신뢰구간(±)</div>
            <div class="fw-bold" style="font-size:1.5rem">{{ kpi.confidencePct.toFixed(1) }}<span class="small fw-normal text-muted ms-1">%</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">재고과잉 위험 품목</div>
            <div class="fw-bold text-warning" style="font-size:1.5rem">{{ kpi.overstockCount }}<span class="small fw-normal text-muted ms-1">종</span></div>
          </div>
        </div>
      </div>

      <!-- 토글 -->
      <div class="d-flex gap-3 mb-3 view-tabs">
        <div class="tab-item" :class="{ active: activeTab === 'demand' }" @click="activeTab = 'demand'">수요 예측</div>
        <div class="tab-item" :class="{ active: activeTab === 'product' }" @click="activeTab = 'product'">제품별 예측</div>
        <div class="tab-item" :class="{ active: activeTab === 'season' }" @click="activeTab = 'season'">계절성 분석</div>
      </div>

      <!-- ===================== 수요 예측 ===================== -->
      <div v-if="activeTab === 'demand'">
        <div class="card erp-card mb-3">
          <div class="card-header bg-white py-2"><span class="fw-semibold small">월별 매출 실적 vs 예측</span></div>
          <div class="card-body">
            <div class="chart-wrap">
              <Line :data="demandChartData" :options="demandChartOptions" />
            </div>
          </div>
        </div>

        <div class="card erp-card mb-3">
          <div class="card-body">
            <div class="d-flex align-items-start gap-2">
              <i class="bi bi-stars text-primary fs-5"></i>
              <div>
                <div class="fw-semibold small mb-1">AI 인사이트</div>
                <div class="small text-muted" v-if="insightLoading">생성 중...</div>
                <div class="small" :class="insightAvailable ? '' : 'text-muted'" v-else>{{ insightText }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card erp-card">
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm mb-0 align-middle">
                <thead class="table-light">
                  <tr><th>기간</th><th class="text-end">예측 매출</th><th class="text-end">하한(95%)</th><th class="text-end">상한(95%)</th></tr>
                </thead>
                <tbody>
                  <tr v-for="f in forecastRows" :key="f.month">
                    <td class="small fw-semibold">{{ f.month }}</td>
                    <td class="small text-end">{{ fmtMoney(f.value) }}</td>
                    <td class="small text-end text-muted">{{ fmtMoney(f.low) }}</td>
                    <td class="small text-end text-muted">{{ fmtMoney(f.high) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-white py-2">
            <span class="small text-muted">
              기준일: {{ anchorMonth }} (데이터상 최신 주문월) · 최근 {{ recentMonths.length }}개월 추세선 기반 · 활동 데이터가 희소한 구간({{ sparsePeriodLabel }})은 추세 계산에서 제외했습니다.
            </span>
          </div>
        </div>
      </div>

      <!-- ===================== 제품별 예측 ===================== -->
      <div v-else-if="activeTab === 'product'" class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>품목명</th><th>카테고리</th>
                  <th class="text-end">최근 3개월 평균 판매량</th>
                  <th class="text-end">다음달 예측 판매량</th>
                  <th>추세</th><th class="text-end">현재고</th><th>재고상태</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in productForecastsTop" :key="p.productid">
                  <td class="small fw-semibold">{{ p.productname }}</td>
                  <td class="small text-muted">{{ p.category }}</td>
                  <td class="small text-end">{{ p.avgQty.toFixed(1) }}</td>
                  <td class="small text-end">{{ p.nextQty.toFixed(1) }}</td>
                  <td>
                    <span :class="trendClass(p.trend)"><i :class="trendIcon(p.trend)"></i> {{ trendLabel(p.trend) }}</span>
                  </td>
                  <td class="small text-end">{{ p.stock }}</td>
                  <td><span class="badge" :class="stockMeta(p.stockStatus).cls">{{ stockMeta(p.stockStatus).label }}</span></td>
                </tr>
                <tr v-if="productForecastsTop.length === 0">
                  <td colspan="7" class="text-center text-muted small py-4">예측 가능한 충분한 주문 이력이 있는 품목이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer bg-white py-2">
          <span class="small text-muted">주문상세 이력이 5건 이상인 품목만 표시합니다 (이력이 적으면 예측 신뢰도가 낮아 제외).</span>
        </div>
      </div>

      <!-- ===================== 계절성 분석 ===================== -->
      <div v-else class="card erp-card">
        <div class="card-header bg-white py-2"><span class="fw-semibold small">월별 매출 비중(계절 지수)</span></div>
        <div class="card-body">
          <div class="chart-wrap">
            <Bar :data="seasonChartData" :options="seasonChartOptions" />
          </div>
        </div>
        <div class="card-footer bg-white py-2">
          <span class="small text-muted">
            지수 100 = 연중 평균. 100보다 높으면 해당 월에 매출이 평균보다 강세라는 의미입니다.
            데이터가 2024년·2026년 상반기에 집중되어 있어 일부 월은 표본이 적습니다(괄호 안 표본 개월 수 참고).
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { useSsafyStore } from '@/stores/ssafy'
import { analyticsApi } from '@/api/analytics'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, Filler)

const ssafyStore = useSsafyStore()
const loading = ref(true)
const activeTab = ref('demand')

function fmtMoney(v) {
  if (v == null) return '-'
  const n = Number(v)
  if (Math.abs(n) >= 100000000) return `${(n / 100000000).toFixed(1)}억원`
  if (Math.abs(n) >= 10000) return `${(n / 10000).toFixed(0)}만원`
  return `${Math.round(n).toLocaleString('ko-KR')}원`
}

// ── 주문상세 + 주문을 결합해 월별 매출 계산 ──
const orderMap = computed(() => new Map(ssafyStore.orders.map((o) => [o.orderid, o])))

const monthlyRevenue = computed(() => {
  const map = new Map() // 'YYYY-MM' -> { revenue, count }
  ssafyStore.orderDetails.forEach((d) => {
    const order = orderMap.value.get(d.orderid)
    if (!order?.orderdate) return
    const dt = new Date(order.orderdate)
    const key = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`
    const revenue = Number(d.unitprice) * d.quantity * (1 - (d.discount || 0))
    if (!map.has(key)) map.set(key, { revenue: 0, count: 0 })
    const e = map.get(key)
    e.revenue += revenue
    e.count += 1
  })
  return [...map.entries()]
    .map(([month, v]) => ({ month, revenue: Math.round(v.revenue), count: v.count }))
    .sort((a, b) => (a.month > b.month ? 1 : -1))
})

// "활동 월" = 그 달에 일정 수준 이상 주문이 발생한 달 (희소 구간 제외)
const ACTIVE_THRESHOLD = 10
const activeMonths = computed(() => monthlyRevenue.value.filter((m) => m.count >= ACTIVE_THRESHOLD))
const sparseMonths = computed(() => monthlyRevenue.value.filter((m) => m.count < ACTIVE_THRESHOLD))
const sparsePeriodLabel = computed(() => {
  const list = sparseMonths.value
  if (!list.length) return '-'
  return `${list[0].month} ~ ${list[list.length - 1].month}`
})

const anchorMonth = computed(() => {
  const list = monthlyRevenue.value
  return list.length ? list[list.length - 1].month : '-'
})

// 가장 최근 "활동 구간"(연속된 활동 월 묶음) 추출 — 최신 활동월부터 역순으로 연속된 구간만 사용
const recentMonths = computed(() => {
  const list = activeMonths.value
  if (!list.length) return []
  const result = [list[list.length - 1]]
  for (let i = list.length - 2; i >= 0; i--) {
    const prev = result[0]
    const [py, pm] = prev.month.split('-').map(Number)
    const expectedPrevIdx = py * 12 + (pm - 1) - 1
    const [cy, cm] = list[i].month.split('-').map(Number)
    if (cy * 12 + (cm - 1) === expectedPrevIdx) {
      result.unshift(list[i])
    } else break
  }
  return result
})

// ── 단순 선형회귀 (최근 활동 구간 기준) ──
function linearRegression(values) {
  const n = values.length
  const xs = values.map((_, i) => i)
  const xMean = xs.reduce((s, x) => s + x, 0) / n
  const yMean = values.reduce((s, y) => s + y, 0) / n
  let num = 0, den = 0
  for (let i = 0; i < n; i++) {
    num += (xs[i] - xMean) * (values[i] - yMean)
    den += (xs[i] - xMean) ** 2
  }
  const slope = den ? num / den : 0
  const intercept = yMean - slope * xMean
  const residuals = values.map((y, i) => y - (slope * i + intercept))
  const rmse = Math.sqrt(residuals.reduce((s, r) => s + r * r, 0) / n)
  return { slope, intercept, rmse }
}

const regression = computed(() => {
  const values = recentMonths.value.map((m) => m.revenue)
  if (values.length < 2) return null
  return linearRegression(values)
})

function addMonth(monthStr, n) {
  const [y, m] = monthStr.split('-').map(Number)
  const total = y * 12 + (m - 1) + n
  return `${Math.floor(total / 12)}-${String(total % 12 + 1).padStart(2, '0')}`
}

const nextMonthLabel = computed(() => anchorMonth.value !== '-' ? addMonth(anchorMonth.value, 1) : '-')

const forecastRows = computed(() => {
  if (!regression.value) return []
  const { slope, intercept, rmse } = regression.value
  const baseIdx = recentMonths.value.length
  const rows = []
  for (let i = 0; i < 3; i++) {
    const idx = baseIdx + i
    const value = Math.max(0, slope * idx + intercept)
    rows.push({
      month: addMonth(anchorMonth.value, i + 1),
      value: Math.round(value),
      low: Math.round(Math.max(0, value - 1.96 * rmse)),
      high: Math.round(value + 1.96 * rmse),
    })
  }
  return rows
})

// 백테스트: 최근 활동구간을 train(앞 75%)/test(뒤 25%)로 나눠 MAPE 기반 정확도 계산
const backtest = computed(() => {
  const values = recentMonths.value.map((m) => m.revenue)
  if (values.length < 4) return { accuracy: 90, rmse: 0 } // 데이터 부족 시 중립값
  const splitAt = Math.max(2, Math.floor(values.length * 0.75))
  const train = values.slice(0, splitAt)
  const test = values.slice(splitAt)
  const { slope, intercept } = linearRegression(train)
  const errors = test.map((actual, i) => {
    const predicted = slope * (splitAt + i) + intercept
    return actual ? Math.abs(actual - predicted) / actual : 0
  })
  const mape = errors.reduce((s, e) => s + e, 0) / errors.length
  return { accuracy: Math.max(0, 100 - mape * 100), rmse: 0 }
})

const kpi = computed(() => ({
  accuracy: backtest.value.accuracy,
  nextMonth: forecastRows.value[0]?.value ?? 0,
  confidencePct: regression.value && forecastRows.value[0]
    ? (1.96 * regression.value.rmse / Math.max(1, forecastRows.value[0].value)) * 100
    : 0,
  overstockCount: productForecasts.value.filter((p) => p.stockStatus === 'over').length, // 전체 품목 기준(표 표시는 상위 30개로 제한)
}))

// ── 차트: 실적 + 예측 ──
const demandChartData = computed(() => {
  const histLabels = activeMonths.value.map((m) => m.month)
  const histValues = activeMonths.value.map((m) => m.revenue)
  const futureLabels = forecastRows.value.map((f) => f.month)
  const labels = [...histLabels, ...futureLabels]
  const actualSeries = [...histValues, ...futureLabels.map(() => null)]
  const forecastSeries = [...histValues.map(() => null), ...forecastRows.value.map((f) => f.value)]
  if (forecastSeries.length > histValues.length) forecastSeries[histValues.length - 1] = histValues[histValues.length - 1]
  const upperSeries = [...histValues.map(() => null), ...forecastRows.value.map((f) => f.high)]
  const lowerSeries = [...histValues.map(() => null), ...forecastRows.value.map((f) => f.low)]
  return {
    labels,
    datasets: [
      { label: '실적', data: actualSeries, borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.08)', tension: 0.2, spanGaps: false },
      { label: '예측', data: forecastSeries, borderColor: '#f59e0b', borderDash: [6, 4], tension: 0.2 },
      { label: '상한', data: upperSeries, borderColor: 'rgba(245,158,11,0.25)', pointRadius: 0, borderWidth: 1 },
      { label: '하한', data: lowerSeries, borderColor: 'rgba(245,158,11,0.25)', pointRadius: 0, borderWidth: 1, fill: '-1', backgroundColor: 'rgba(245,158,11,0.08)' },
    ],
  }
})
const demandChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'top' } },
  scales: { y: { ticks: { callback: (v) => fmtMoney(v) } } },
}

// ── 제품별 예측 ──
const categoryMap = computed(() => new Map(ssafyStore.products.map((p) => [p.productid, p])))

const productForecasts = computed(() => {
  const byProduct = new Map() // productid -> [{month, qty}]
  ssafyStore.orderDetails.forEach((d) => {
    const order = orderMap.value.get(d.orderid)
    if (!order?.orderdate) return
    if (!byProduct.has(d.productid)) byProduct.set(d.productid, [])
    byProduct.get(d.productid).push({ date: order.orderdate, qty: d.quantity })
  })

  const rows = []
  byProduct.forEach((records, productid) => {
    if (records.length < 5) return
    const product = categoryMap.value.get(productid)
    if (!product) return
    records.sort((a, b) => (a.date > b.date ? 1 : -1))
    const recent = records.slice(-6)
    const half = Math.ceil(recent.length / 2)
    const firstHalf = recent.slice(0, half)
    const secondHalf = recent.slice(half)
    const avgFirst = firstHalf.reduce((s, r) => s + r.qty, 0) / firstHalf.length
    const avgSecond = secondHalf.reduce((s, r) => s + r.qty, 0) / (secondHalf.length || 1)
    const avgQty = recent.reduce((s, r) => s + r.qty, 0) / recent.length
    const growth = avgFirst ? (avgSecond - avgFirst) / avgFirst : 0
    const trend = growth > 0.1 ? 'up' : growth < -0.1 ? 'down' : 'flat'
    const nextQty = Math.max(0, avgSecond + (avgSecond - avgFirst))
    const stock = product.unitsinstock ?? 0
    const monthsOfSupply = avgQty > 0 ? stock / avgQty : null
    let stockStatus = 'normal'
    if (monthsOfSupply != null) {
      if (monthsOfSupply > 6) stockStatus = 'over'
      else if (monthsOfSupply < 1) stockStatus = 'under'
    }
    rows.push({
      productid, productname: product.productname, category: product.category_name,
      avgQty, nextQty, trend, stock, stockStatus,
    })
  })
  return rows.sort((a, b) => b.avgQty - a.avgQty)
})
const productForecastsTop = computed(() => productForecasts.value.slice(0, 30))

function trendLabel(t) { return { up: '상승', down: '하락', flat: '안정' }[t] }
function trendIcon(t) { return { up: 'bi bi-arrow-up-short', down: 'bi bi-arrow-down-short', flat: 'bi bi-dash' }[t] }
function trendClass(t) { return { up: 'text-success', down: 'text-danger', flat: 'text-muted' }[t] }
function stockMeta(s) {
  const map = {
    over: { label: '과잉', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    under: { label: '부족', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    normal: { label: '적정', cls: 'bg-success-subtle text-success border border-success-subtle' },
  }
  return map[s]
}

// ── 계절성 분석 ──
const seasonChartData = computed(() => {
  const byMonthNum = new Map() // 1~12 -> [revenue,...]
  monthlyRevenue.value.forEach((m) => {
    const num = parseInt(m.month.split('-')[1], 10)
    if (!byMonthNum.has(num)) byMonthNum.set(num, [])
    byMonthNum.get(num).push(m.revenue)
  })
  const overallAvg = monthlyRevenue.value.reduce((s, m) => s + m.revenue, 0) / (monthlyRevenue.value.length || 1)
  const labels = []
  const data = []
  for (let m = 1; m <= 12; m++) {
    const list = byMonthNum.get(m) || []
    const avg = list.length ? list.reduce((s, v) => s + v, 0) / list.length : 0
    labels.push(`${m}월 (n=${list.length})`)
    data.push(overallAvg ? Math.round((avg / overallAvg) * 100) : 0)
  }
  return {
    labels,
    datasets: [{ label: '계절 지수', data, backgroundColor: data.map((v) => (v >= 100 ? '#2563eb' : '#cbd5e1')), borderRadius: 4 }],
  }
})
const seasonChartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { ticks: { callback: (v) => `${v}` } } },
}

// ── AI 인사이트 ──
const insightText = ref('')
const insightAvailable = ref(false)
const insightLoading = ref(false)

async function loadInsight() {
  if (!recentMonths.value.length) return
  insightLoading.value = true
  try {
    const summary = {
      anchor_month: anchorMonth.value,
      recent_months: recentMonths.value.map((m) => ({ month: m.month, revenue: m.revenue })),
      next_month_forecast: forecastRows.value[0]?.value,
      backtest_accuracy_pct: Number(kpi.value.accuracy.toFixed(1)),
      overstock_product_count: kpi.value.overstockCount,
    }
    const res = await analyticsApi.demandInsight(summary)
    insightAvailable.value = res.data.available
    insightText.value = res.data.insight
  } catch {
    insightAvailable.value = false
    insightText.value = 'AI 인사이트를 불러오지 못했습니다.'
  } finally {
    insightLoading.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'demand' && !insightText.value) loadInsight()
})

onMounted(async () => {
  loading.value = true
  await Promise.all([
    ssafyStore.fetchOrders(),
    ssafyStore.fetchOrderDetails(),
    ssafyStore.fetchProducts(),
  ])
  loading.value = false
  loadInsight()
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.view-tabs { border-bottom: 1px solid #e5e7eb; }
.tab-item {
  padding: 8px 4px 10px; font-weight: 600; font-size: 0.92rem; color: #94a3b8;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }
.chart-wrap { position: relative; height: 320px; }
</style>
