<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-building me-2"></i>거래처관리</h5>
        <p class="text-muted small mb-0">거래처 기본정보를 등록·조회·수정·삭제합니다</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i>거래처 등록
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">전체 거래처</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ kpi.total }}<span class="small fw-normal text-muted ms-1">개</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">활성 거래처</div>
          <div class="fw-bold text-success" style="font-size:1.6rem">{{ kpi.active }}<span class="small fw-normal text-muted ms-1">개</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">휴면 거래처</div>
          <div class="fw-bold text-secondary" style="font-size:1.6rem">{{ kpi.dormant }}<span class="small fw-normal text-muted ms-1">개</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">진출 지역 수</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ kpi.cityCount }}<span class="small fw-normal text-muted ms-1">개</span></div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-4">
            <label class="form-label small text-muted mb-1">거래처명</label>
            <input v-model="draft.search" type="text" class="form-control form-control-sm" placeholder="회사명, 담당자 검색" />
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">지역</label>
            <select v-model="draft.region" class="form-select form-select-sm">
              <option value="">전체</option>
              <option v-for="r in regionOptions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="draft.status" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="active">활성</option>
              <option value="dormant">휴면</option>
            </select>
          </div>
          <div class="col-md-3 d-flex gap-2">
            <button class="btn btn-sm btn-primary flex-grow-1" @click="applyFilters"><i class="bi bi-search me-1"></i>조회</button>
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="resetFilters"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="ssafyStore.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>코드</th><th>거래처명</th><th>담당자</th><th>도시</th><th>지역</th>
                <th>전화</th><th class="text-end">주문수</th><th>상태</th><th>관리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in pagedRows" :key="c.customerid">
                <td class="small text-muted cursor-pointer" @click="goDetail(c.customerid)">{{ c.customerid }}</td>
                <td class="small fw-semibold cursor-pointer" @click="goDetail(c.customerid)">{{ c.companyname }}</td>
                <td class="small">{{ c.contactname || '-' }}</td>
                <td class="small text-muted">{{ c.city || '-' }}</td>
                <td class="small text-muted">{{ c.region || '-' }}</td>
                <td class="small text-muted">{{ c.phone || '-' }}</td>
                <td class="small text-end">{{ orderCount(c.customerid) }}</td>
                <td>
                  <span class="badge" :class="orderCount(c.customerid) > 0 ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border border-secondary-subtle'">
                    {{ orderCount(c.customerid) > 0 ? '활성' : '휴면' }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn-icon" title="수정" @click="openEditModal(c)"><i class="bi bi-pencil"></i></button>
                    <button class="btn-icon text-danger" title="삭제" @click="deleteCustomer(c)"><i class="bi bi-trash"></i></button>
                  </div>
                </td>
              </tr>
              <tr v-if="pagedRows.length === 0">
                <td colspan="9" class="text-center text-muted small py-4">조건에 맞는 거래처가 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer d-flex justify-content-between align-items-center py-2 bg-white">
        <span class="small text-muted">총 {{ filteredRows.length.toLocaleString('ko-KR') }}건 중 {{ pageStart + 1 }}-{{ pageEnd }}</span>
        <div class="d-flex gap-1 align-items-center">
          <button class="btn btn-sm btn-outline-secondary" :disabled="page === 1" @click="page--"><i class="bi bi-chevron-left"></i></button>
          <span class="small mx-2">{{ page }} / {{ totalPages }}</span>
          <button class="btn btn-sm btn-outline-secondary" :disabled="page === totalPages" @click="page++"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>
    </div>

    <!-- 등록/수정 모달 -->
    <Teleport to="body">
      <div v-if="showFormModal" class="modal-backdrop-custom" @click.self="showFormModal = false">
        <div class="modal-panel shadow-lg" style="width:480px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-building me-2 text-primary"></i>{{ editingId ? '거래처 수정' : '거래처 등록' }}</span>
            <button class="btn-close-panel" @click="showFormModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="row g-2 mb-3">
              <div class="col-5">
                <label class="form-label small fw-semibold">코드</label>
                <input v-model="form.customerid" type="text" class="form-control form-control-sm" :disabled="!!editingId" />
              </div>
              <div class="col-7">
                <label class="form-label small fw-semibold">회사명 <span class="text-danger">*</span></label>
                <input v-model="form.companyname" type="text" class="form-control form-control-sm" />
              </div>
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
              <div class="col-4">
                <label class="form-label small fw-semibold">도시</label>
                <input v-model="form.city" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-4">
                <label class="form-label small fw-semibold">지역</label>
                <input v-model="form.region" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-4">
                <label class="form-label small fw-semibold">우편번호</label>
                <input v-model="form.postalcode" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-4">
                <label class="form-label small fw-semibold">국가</label>
                <input v-model="form.country" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-4">
                <label class="form-label small fw-semibold">전화 <span class="text-danger">*</span></label>
                <input v-model="form.phone" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-4">
                <label class="form-label small fw-semibold">팩스</label>
                <input v-model="form.fax" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div v-if="formError" class="alert alert-danger small py-2 mb-0">{{ formError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showFormModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="saving" @click="submitForm">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>{{ editingId ? '수정' : '등록' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSsafyStore } from '@/stores/ssafy'
import { ssafyApi } from '@/api/ssafy'

const router = useRouter()
const ssafyStore = useSsafyStore()

const draft = reactive({ search: '', region: '', status: '' })
const applied = reactive({ search: '', region: '', status: '' })
const page = ref(1)
const pageSize = 15

const orderCountMap = computed(() => {
  const m = new Map()
  ssafyStore.orders.forEach((o) => m.set(o.customerid, (m.get(o.customerid) || 0) + 1))
  return m
})
function orderCount(customerid) {
  return orderCountMap.value.get(customerid) || 0
}

const regionOptions = computed(() => [...new Set(ssafyStore.customers.map((c) => c.region).filter(Boolean))].sort())

const kpi = computed(() => {
  const list = ssafyStore.customers
  const active = list.filter((c) => orderCount(c.customerid) > 0).length
  return {
    total: list.length,
    active,
    dormant: list.length - active,
    cityCount: new Set(list.map((c) => c.city).filter(Boolean)).size,
  }
})

const filteredRows = computed(() => {
  let list = ssafyStore.customers
  if (applied.search) {
    const q = applied.search.toLowerCase()
    list = list.filter((c) => (c.companyname || '').toLowerCase().includes(q) || (c.contactname || '').toLowerCase().includes(q))
  }
  if (applied.region) list = list.filter((c) => c.region === applied.region)
  if (applied.status === 'active') list = list.filter((c) => orderCount(c.customerid) > 0)
  else if (applied.status === 'dormant') list = list.filter((c) => orderCount(c.customerid) === 0)
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize)))
const pageStart = computed(() => (page.value - 1) * pageSize)
const pageEnd = computed(() => Math.min(filteredRows.value.length, pageStart.value + pageSize))
const pagedRows = computed(() => filteredRows.value.slice(pageStart.value, pageEnd.value))

watch(() => [applied.search, applied.region, applied.status], () => { page.value = 1 })

function applyFilters() { Object.assign(applied, draft); page.value = 1 }
function resetFilters() {
  draft.search = ''; draft.region = ''; draft.status = ''
  applied.search = ''; applied.region = ''; applied.status = ''
}

function goDetail(id) { router.push(`/customers/${id}`) }

// ── 등록/수정 ──
const showFormModal = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)

function blankForm() {
  return { customerid: '', companyname: '', contactname: '', contacttitle: '', address: '', city: '', region: '', postalcode: '', country: '한국', phone: '', fax: '' }
}
const form = reactive(blankForm())

function nextCustomerId() {
  let max = 0
  ssafyStore.customers.forEach((c) => {
    const m = /SI(\d+)/.exec(c.customerid)
    if (m) max = Math.max(max, parseInt(m[1], 10))
  })
  return `SI${String(max + 1).padStart(3, '0')}`
}

function openCreateModal() {
  Object.assign(form, blankForm())
  form.customerid = nextCustomerId()
  editingId.value = null
  formError.value = ''
  showFormModal.value = true
}

function openEditModal(c) {
  Object.assign(form, blankForm(), c)
  editingId.value = c.customerid
  formError.value = ''
  showFormModal.value = true
}

async function submitForm() {
  if (!form.customerid || !form.companyname || !form.phone) {
    formError.value = '코드, 회사명, 전화번호를 입력하세요.'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editingId.value) {
      await ssafyApi.updateCustomer(editingId.value, form)
    } else {
      await ssafyApi.createCustomer(form)
    }
    showFormModal.value = false
    await ssafyStore.fetchCustomers()
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}

async function deleteCustomer(c) {
  if (!confirm(`${c.companyname} 거래처를 삭제하시겠습니까?`)) return
  try {
    await ssafyApi.deleteCustomer(c.customerid)
    await ssafyStore.fetchCustomers()
  } catch {
    alert('이 거래처와 연결된 주문 내역이 있어 삭제할 수 없습니다.')
  }
}

onMounted(() => {
  ssafyStore.fetchCustomers()
  ssafyStore.fetchOrders()
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.cursor-pointer { cursor: pointer; }
.btn-icon { border: none; background: transparent; color: #64748b; padding: 2px 6px; border-radius: 6px; cursor: pointer; }
.btn-icon:hover { background: #f1f5f9; color: #1e293b; }

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
