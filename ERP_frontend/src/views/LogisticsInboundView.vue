<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-box-arrow-in-down me-2"></i>입고관리</h5>
        <p class="text-muted small mb-0">
          상품 입고를 등록하고 검수 처리 현황을 관리합니다.
          <span class="text-primary fw-semibold ms-1">· 최근 7일({{ recentRangeLabel }}) 기준</span>
        </p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i>입고등록
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">최근입고(7일)</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.recent }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-primary-subtle text-primary"><i class="bi bi-box-seam"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">검수대기</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.hold }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-warning-subtle text-warning"><i class="bi bi-patch-check"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">반려/불량</div>
              <div class="fw-bold text-danger" style="font-size:1.6rem">{{ stats.reject }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-danger-subtle text-danger"><i class="bi bi-exclamation-triangle"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">입고완료({{ currentYear }})</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.pass }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-success-subtle text-success"><i class="bi bi-check-circle"></i></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-4">
            <label class="form-label small text-muted mb-1">검색</label>
            <input v-model="search" type="text" class="form-control form-control-sm" placeholder="품목명 / 입고번호 / 공급업체" />
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="statusFilter" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="hold">검수대기</option>
              <option value="pass">입고완료</option>
              <option value="reject">반려/불량</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">입고창고</label>
            <select v-model="warehouseFilter" class="form-select form-select-sm">
              <option value="">전체</option>
              <option v-for="w in warehouseOptions" :key="w" :value="w">{{ w }}</option>
            </select>
          </div>
          <div class="col-md-2 d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary w-100" @click="resetFilters">
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
                <th class="cursor-pointer" @click="toggleSort('id')">입고번호 <i :class="sortIcon('id')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('product_name')">품목 <i :class="sortIcon('product_name')"></i></th>
                <th>유형</th>
                <th class="text-end">입고수량</th>
                <th>발주번호</th>
                <th class="cursor-pointer" @click="toggleSort('orderdate')">발주일 <i :class="sortIcon('orderdate')"></i></th>
                <th>입고창고</th>
                <th>상태</th>
                <th class="cursor-pointer" @click="toggleSort('receiptdate')">입고일 <i :class="sortIcon('receiptdate')"></i></th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pagedRows" :key="row.id">
                <td class="small text-muted">{{ row.code }}</td>
                <td class="small">
                  <div class="fw-semibold">{{ row.product_name }}</div>
                  <div class="text-muted" style="font-size:0.72rem">#{{ row.productid }} · {{ row.supplier_name || '-' }}</div>
                </td>
                <td><span class="badge bg-light text-dark border">{{ row.category_name || '-' }}</span></td>
                <td class="small text-end">
                  <div class="fw-semibold">{{ row.quantityreceived?.toLocaleString('ko-KR') }}</div>
                  <div v-if="row.quantityreceived !== row.quantityordered" class="text-danger" style="font-size:0.72rem">
                    / {{ row.quantityordered?.toLocaleString('ko-KR') }} 중 부족
                  </div>
                </td>
                <td class="small text-muted">{{ row.poCode }}</td>
                <td class="small text-muted">{{ fmtDate(row.orderdate) }}</td>
                <td><span class="badge bg-light text-dark border">{{ row.warehouse || '-' }}</span></td>
                <td><span class="badge" :class="statusMeta(row.qcstatus).cls">{{ statusMeta(row.qcstatus).label }}</span></td>
                <td class="small text-muted">{{ fmtDate(row.receiptdate) }}</td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn-icon" title="수정" @click="openEditModal(row)"><i class="bi bi-pencil"></i></button>
                    <button class="btn-icon text-danger" title="삭제" @click="deleteReceipt(row.id)"><i class="bi bi-trash"></i></button>
                  </div>
                </td>
              </tr>
              <tr v-if="pagedRows.length === 0">
                <td colspan="10" class="text-center text-muted small py-4">조건에 맞는 입고 내역이 없습니다</td>
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

    <!-- 입고등록 / 수정 모달 -->
    <Teleport to="body">
      <div v-if="showFormModal" class="modal-backdrop-custom" @click.self="showFormModal = false">
        <div class="modal-panel shadow-lg" style="width:480px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-box-seam me-2 text-primary"></i>{{ editingId ? '입고 수정' : '입고등록' }}</span>
            <button class="btn-close-panel" @click="showFormModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">발주(PO) <span class="text-danger">*</span></label>
              <select v-model="form.poId" class="form-select form-select-sm" :disabled="!!editingId" @change="onPoChange">
                <option value="">선택</option>
                <option v-for="po in poOptions" :key="po.id" :value="po.id">
                  PO-{{ String(po.id).padStart(6, '0') }} · {{ po.supplier_name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">품목 <span class="text-danger">*</span></label>
              <select v-model="form.productid" class="form-select form-select-sm" :disabled="!!editingId" @change="onProductChange">
                <option value="">선택</option>
                <option v-for="d in poLineOptions" :key="d.productid" :value="d.productid">
                  {{ d.product_name }} (발주수량 {{ d.quantity }})
                </option>
              </select>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">발주수량</label>
                <input v-model.number="form.quantityordered" type="number" min="0" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">입고수량 <span class="text-danger">*</span></label>
                <input v-model.number="form.quantityreceived" type="number" min="0" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">검수상태</label>
                <select v-model="form.qcstatus" class="form-select form-select-sm">
                  <option value="hold">검수대기</option>
                  <option value="pass">입고완료</option>
                  <option value="reject">반려/불량</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">입고창고</label>
                <select v-model="form.warehouse" class="form-select form-select-sm">
                  <option v-for="w in warehouseOptions" :key="w" :value="w">{{ w }}</option>
                </select>
              </div>
            </div>
            <div class="mb-1">
              <label class="form-label small fw-semibold">입고일</label>
              <input v-model="form.receiptdate" type="date" class="form-control form-control-sm" />
            </div>
            <div v-if="formError" class="alert alert-danger small py-2 mt-3 mb-0">{{ formError }}</div>
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
import { useProcurementStore } from '@/stores/procurement'
import { procurementApi } from '@/api/procurement'
import { ssafyApi } from '@/api/ssafy'

const store = useProcurementStore()

const warehouseOptions = ['경기물류센터', '중앙물류센터', '부산물류센터']

const search = ref('')
const statusFilter = ref('')
const warehouseFilter = ref('')
const sortKey = ref('receiptdate')
const sortDir = ref('desc')
const currentPage = ref(1)
const pageSize = 15

const products = ref([])

// ── "최근입고": 오늘 기준 최근 7일(오늘 포함) 이내 입고 건수 ──
const currentYear = new Date().getFullYear()
function daysAgoStr(n) {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}
const recentRangeLabel = computed(() => `${fmtDate(daysAgoStr(6))} ~ ${fmtDate(todayStr())}`)

// ── 목록 구성: GoodsReceipt + 발주(PurchaseOrder) 헤더 + 상품 카테고리 결합 ──
const rows = computed(() => {
  const productMap = new Map(products.value.map((p) => [p.productid, p]))
  return store.goodsReceipts.map((gr) => {
    const po = store.purchaseOrders.find((p) => p.id === gr.purchaseorderid)
    const product = productMap.get(gr.productid)
    return {
      id: gr.id,
      code: `IB-${String(gr.id).padStart(6, '0')}`,
      productid: gr.productid,
      product_name: gr.product_name,
      supplier_name: po?.supplier_name,
      category_name: product?.category_name,
      quantityordered: gr.quantityordered,
      quantityreceived: gr.quantityreceived,
      poId: gr.purchaseorderid,
      poCode: po ? `PO-${String(po.id).padStart(6, '0')}` : '-',
      orderdate: po?.orderdate,
      warehouse: gr.warehouse,
      qcstatus: gr.qcstatus,
      receiptdate: gr.receiptdate,
    }
  })
})

const filteredRows = computed(() => {
  let list = rows.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(
      (r) =>
        (r.product_name || '').toLowerCase().includes(q) ||
        (r.code || '').toLowerCase().includes(q) ||
        (r.supplier_name || '').toLowerCase().includes(q),
    )
  }
  if (statusFilter.value) list = list.filter((r) => r.qcstatus === statusFilter.value)
  if (warehouseFilter.value) list = list.filter((r) => r.warehouse === warehouseFilter.value)
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

watch([search, statusFilter, warehouseFilter], () => {
  currentPage.value = 1
})

const stats = computed(() => {
  const list = store.goodsReceipts
  const weekAgo = daysAgoStr(6)
  const today = todayStr()
  return {
    recent: list.filter((g) => g.receiptdate && g.receiptdate >= weekAgo && g.receiptdate <= today).length,
    hold: list.filter((g) => g.qcstatus === 'hold').length,
    reject: list.filter((g) => g.qcstatus === 'reject').length,
    pass: list.filter((g) => g.qcstatus === 'pass' && g.receiptdate && new Date(g.receiptdate).getFullYear() === currentYear).length,
  }
})

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

function resetFilters() {
  search.value = ''
  statusFilter.value = ''
  warehouseFilter.value = ''
}

function statusMeta(qcstatus) {
  const map = {
    hold: { label: '검수대기', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    pass: { label: '입고완료', cls: 'bg-success-subtle text-success border border-success-subtle' },
    reject: { label: '반려/불량', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
  }
  return map[qcstatus] || { label: qcstatus || '-', cls: 'bg-secondary-subtle text-secondary' }
}

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}
function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

// ── 입고등록 / 수정 / 삭제 ──
const showFormModal = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = reactive({
  poId: '',
  productid: '',
  quantityordered: 0,
  quantityreceived: 0,
  qcstatus: 'pass',
  warehouse: warehouseOptions[0],
  receiptdate: todayStr(),
})

// 발주완료 처리된(received/partial) PO만 입고 등록 대상으로 노출
const poOptions = computed(() => store.purchaseOrders.filter((po) => po.status !== 'ordered'))
const poLineOptions = computed(() => {
  const po = store.purchaseOrders.find((p) => p.id === form.poId)
  return po?.details || []
})

function onPoChange() {
  form.productid = ''
  form.quantityordered = 0
  form.quantityreceived = 0
}
function onProductChange() {
  const line = poLineOptions.value.find((d) => d.productid === form.productid)
  if (line) {
    form.quantityordered = line.quantity
    form.quantityreceived = line.quantity
  }
}

function openCreateModal() {
  editingId.value = null
  form.poId = ''
  form.productid = ''
  form.quantityordered = 0
  form.quantityreceived = 0
  form.qcstatus = 'pass'
  form.warehouse = warehouseOptions[0]
  form.receiptdate = todayStr()
  formError.value = ''
  showFormModal.value = true
}

function openEditModal(row) {
  editingId.value = row.id
  form.poId = row.poId
  form.productid = row.productid
  form.quantityordered = row.quantityordered
  form.quantityreceived = row.quantityreceived
  form.qcstatus = row.qcstatus
  form.warehouse = row.warehouse || warehouseOptions[0]
  form.receiptdate = row.receiptdate
  formError.value = ''
  showFormModal.value = true
}

async function submitForm() {
  if (!form.poId || !form.productid) {
    formError.value = '발주와 품목을 선택하세요.'
    return
  }
  if (!form.quantityreceived || form.quantityreceived < 0) {
    formError.value = '입고수량을 입력하세요.'
    return
  }
  saving.value = true
  formError.value = ''
  const payload = {
    purchaseorderid: form.poId,
    productid: form.productid,
    receiptdate: form.receiptdate,
    quantityordered: Number(form.quantityordered) || 0,
    quantityreceived: Number(form.quantityreceived),
    qcstatus: form.qcstatus,
    warehouse: form.warehouse,
  }
  try {
    if (editingId.value) {
      await procurementApi.updateGoodsReceipt(editingId.value, payload)
    } else {
      await procurementApi.createGoodsReceipt(payload)
    }
    showFormModal.value = false
    await store.fetchAll()
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}

async function deleteReceipt(id) {
  if (!confirm(`IB-${String(id).padStart(6, '0')} 입고 내역을 삭제하시겠습니까?`)) return
  try {
    await procurementApi.deleteGoodsReceipt(id)
    await store.fetchAll()
  } catch {
    alert('삭제에 실패했습니다.')
  }
}

onMounted(async () => {
  store.fetchAll()
  const res = await ssafyApi.products()
  products.value = res.data
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.kpi-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.cursor-pointer { cursor: pointer; user-select: none; }
.btn-icon {
  border: none; background: transparent; color: #64748b; padding: 2px 6px; border-radius: 6px; cursor: pointer;
}
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
