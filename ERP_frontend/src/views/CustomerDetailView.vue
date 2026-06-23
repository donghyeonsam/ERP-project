<template>
  <div style="max-width:720px">
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-sm btn-outline-secondary" @click="$router.back()"><i class="bi bi-arrow-left"></i></button>
      <h5 class="fw-bold mb-0">고객사 상세</h5>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else-if="customer" class="row g-3">
      <div class="col-12">
        <div class="card erp-card">
          <div class="card-body">
            <h6 class="fw-bold mb-3">{{ customer.companyname }}</h6>
            <div class="row g-2">
              <div class="col-md-6" v-for="f in fields" :key="f.label">
                <div class="small text-muted">{{ f.label }}</div>
                <div class="small fw-semibold">{{ f.value || '-' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Orders for this customer -->
      <div class="col-12">
        <div class="card erp-card">
          <div class="card-header py-2"><span class="fw-semibold small">주문 내역</span></div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm table-hover mb-0">
                <thead class="table-light"><tr><th>주문ID</th><th>주문일</th><th>배송일</th><th>상태</th></tr></thead>
                <tbody>
                  <tr v-for="o in customerOrders" :key="o.orderid">
                    <td class="small fw-semibold">{{ o.orderid }}</td>
                    <td class="small text-muted">{{ fmtDate(o.orderdate) }}</td>
                    <td class="small text-muted">{{ fmtDate(o.shippeddate) }}</td>
                    <td><span :class="['badge', o.shippeddate ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning']">{{ o.shippeddate ? '완료' : '처리중' }}</span></td>
                  </tr>
                  <tr v-if="customerOrders.length === 0"><td colspan="4" class="text-center text-muted small py-3">주문 없음</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ssafyApi } from '@/api/ssafy'
import { useSsafyStore } from '@/stores/ssafy'

const route = useRoute()
const ssafyStore = useSsafyStore()
const customer = ref(null)
const loading = ref(false)

const customerOrders = computed(() =>
  ssafyStore.orders.filter(o => o.customerid === route.params.id),
)

const fields = computed(() => [
  { label: '고객ID', value: customer.value?.customerid },
  { label: '담당자', value: customer.value?.contactname },
  { label: '직책', value: customer.value?.contacttitle },
  { label: '주소', value: customer.value?.address },
  { label: '도시', value: customer.value?.city },
  { label: '국가', value: customer.value?.country },
  { label: '전화', value: customer.value?.phone },
  { label: '팩스', value: customer.value?.fax },
])

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

onMounted(async () => {
  loading.value = true
  try {
    const [cRes] = await Promise.all([
      ssafyApi.customer(route.params.id),
      ssafyStore.fetchOrders({ customerid: route.params.id }),
    ])
    customer.value = cRes.data
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
</style>
