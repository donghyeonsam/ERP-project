<template>
  <div style="max-width:720px">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div class="d-flex align-items-center gap-2">
        <button class="btn btn-sm btn-outline-secondary" @click="$router.back()"><i class="bi bi-arrow-left"></i></button>
        <h5 class="fw-bold mb-0">거래처 상세</h5>
      </div>
      <button v-if="customer" class="btn btn-sm btn-outline-primary" @click="openEditModal"><i class="bi bi-pencil me-1"></i>수정</button>
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

    <!-- 수정 모달 -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-backdrop-custom" @click.self="showEditModal = false">
        <div class="modal-panel shadow-lg" style="width:480px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-building me-2 text-primary"></i>거래처 수정</span>
            <button class="btn-close-panel" @click="showEditModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">회사명 <span class="text-danger">*</span></label>
              <input v-model="form.companyname" type="text" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">담당자</label>
                <input v-model="form.contactname" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">직책</label>
                <input v-model="form.contacttitle" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">주소</label>
              <input v-model="form.address" type="text" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">도시</label>
                <input v-model="form.city" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">국가</label>
                <input v-model="form.country" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">전화</label>
                <input v-model="form.phone" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">팩스</label>
                <input v-model="form.fax" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div v-if="formError" class="alert alert-danger small py-2 mb-0">{{ formError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showEditModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="saving" @click="submitEdit">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>수정
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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

// ── 수정 ──
const showEditModal = ref(false)
const saving = ref(false)
const formError = ref('')
const form = reactive({ companyname: '', contactname: '', contacttitle: '', address: '', city: '', country: '', phone: '', fax: '' })

function openEditModal() {
  Object.assign(form, customer.value)
  formError.value = ''
  showEditModal.value = true
}

async function submitEdit() {
  if (!form.companyname) {
    formError.value = '회사명을 입력하세요.'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const res = await ssafyApi.updateCustomer(route.params.id, form)
    customer.value = res.data
    showEditModal.value = false
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}

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

.modal-backdrop-custom {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4);
  display: flex; align-items: center; justify-content: center; z-index: 1300;
}
.modal-panel {
  max-height: 88vh; background: #fff; border-radius: 14px;
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-panel-header {
  padding: 14px 16px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #f1f5f9; background: #fff;
}
.btn-close-panel { border: none; background: transparent; color: #94a3b8; font-size: 0.9rem; cursor: pointer; }
.btn-close-panel:hover { color: #374151; }
.modal-panel-body { flex: 1; overflow-y: auto; padding: 16px; }
.modal-panel-footer { padding: 12px 16px; border-top: 1px solid #f1f5f9; }
</style>
