<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0">구매 대시보드</h5>
        <p class="text-muted small mb-0">Procurement Dashboard</p>
      </div>
      <button class="btn btn-sm btn-outline-primary"><i class="bi bi-printer me-1"></i>보고서 출력</button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">발주 건수</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ store.purchaseOrders.length }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">자재 종류</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ store.materials.length }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">입고 완료</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ store.goodsReceipts.length }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <!-- TODO: no backend endpoint for PO amount total -->
        <div class="card erp-card text-center p-3">
          <div class="text-muted small mb-1">발주 총액</div>
          <div class="fw-bold text-muted" style="font-size:1.6rem">--</div>
        </div>
      </div>
    </div>

    <!-- PO Status + Materials -->
    <div class="row g-3 mb-4">
      <div class="col-md-5">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">발주 현황</span>
          </div>
          <div class="card-body d-flex align-items-center justify-content-center">
            <Doughnut :data="poStatusChart" :options="donutOptions" style="max-height:200px" />
          </div>
        </div>
      </div>
      <div class="col-md-7">
        <div class="card erp-card">
          <div class="card-header py-2">
            <span class="fw-semibold small">자재 재고 현황</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive" style="max-height:220px;overflow-y:auto">
              <table class="table table-sm table-hover mb-0">
                <thead class="table-light">
                  <tr><th>자재ID</th><th>자재명</th><th>재고</th><th>단위</th></tr>
                </thead>
                <tbody>
                  <tr v-for="m in store.materials.slice(0,10)" :key="m.materialid">
                    <td class="small text-muted">{{ m.materialid }}</td>
                    <td class="small">{{ m.materialname || m.name }}</td>
                    <td class="small fw-semibold">{{ m.quantity || m.stock || '--' }}</td>
                    <td class="small text-muted">{{ m.unit || '--' }}</td>
                  </tr>
                  <tr v-if="store.materials.length === 0">
                    <td colspan="4" class="text-center text-muted small py-3">데이터 없음</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Goods Receipt Table -->
    <div class="card erp-card">
      <div class="card-header py-2">
        <span class="fw-semibold small">입고 현황</span>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>입고ID</th><th>발주ID</th><th>자재ID</th><th>입고수량</th><th>입고일</th></tr>
            </thead>
            <tbody>
              <tr v-for="gr in store.goodsReceipts.slice(0,15)" :key="gr.id">
                <td class="small">{{ gr.id }}</td>
                <td class="small">{{ gr.purchase_order || gr.purchaseorderid }}</td>
                <td class="small">{{ gr.material || gr.materialid }}</td>
                <td class="small fw-semibold">{{ gr.quantity }}</td>
                <td class="small text-muted">{{ fmtDate(gr.receipt_date || gr.receiptdate) }}</td>
              </tr>
              <tr v-if="store.goodsReceipts.length === 0">
                <td colspan="5" class="text-center text-muted small py-3">데이터 없음</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Purchase Orders -->
    <div class="card erp-card mt-3">
      <div class="card-header py-2">
        <span class="fw-semibold small">발주 목록</span>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>발주ID</th><th>공급업체</th><th>발주일</th><th>납기일</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="po in store.purchaseOrders.slice(0,10)" :key="po.id">
                <td class="small">{{ po.id }}</td>
                <td class="small">{{ po.supplier || po.supplierid }}</td>
                <td class="small text-muted">{{ fmtDate(po.order_date || po.orderdate) }}</td>
                <td class="small text-muted">{{ fmtDate(po.due_date || po.duedate) }}</td>
                <td>
                  <span :class="['badge', po.status === '완료' ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning']">
                    {{ po.status || '처리중' }}
                  </span>
                </td>
              </tr>
              <tr v-if="store.purchaseOrders.length === 0">
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
import { computed, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { useProcurementStore } from '@/stores/procurement'

ChartJS.register(ArcElement, Tooltip, Legend)

const store = useProcurementStore()

const poStatusChart = computed(() => ({
  labels: ['완료', '처리중', '지연'],
  datasets: [{
    data: [
      store.purchaseOrders.filter(p => p.status === '완료').length || 1,
      store.purchaseOrders.filter(p => !p.status || p.status === '처리중').length || 1,
      store.purchaseOrders.filter(p => p.status === '지연').length || 0,
    ],
    backgroundColor: ['#10b981', '#2563eb', '#ef4444'],
    borderWidth: 0,
  }],
}))

const donutOptions = { responsive: true, plugins: { legend: { position: 'bottom' } } }

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}

onMounted(() => store.fetchAll())
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
