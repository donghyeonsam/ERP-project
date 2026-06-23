<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-file-earmark-text me-2"></i>발주관리</h5>
        <p class="text-muted small mb-0">
          상품 구매요청 접수 및 발주 처리 현황을 관리합니다.
          <span v-if="latestMonthLabel" class="text-primary fw-semibold ms-1">· {{ latestMonthLabel }} 기준</span>
        </p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i>발주등록
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">이번달 발주건수</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.total }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-primary-subtle text-primary"><i class="bi bi-cart3"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">발주대기(미입고)</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.pending }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-warning-subtle text-warning"><i class="bi bi-clock-history"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">지연 발주</div>
              <div class="fw-bold text-danger" style="font-size:1.6rem">{{ stats.overdue }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-danger-subtle text-danger"><i class="bi bi-exclamation-triangle"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">이번달 발주금액</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ fmtMoney(stats.totalAmount) }}</div>
            </div>
            <div class="kpi-icon bg-info-subtle text-info"><i class="bi bi-file-earmark-bar-graph"></i></div>
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
            <input v-model="search" type="text" class="form-control form-control-sm" placeholder="품목명 / 발주번호 / 공급업체" />
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="statusFilter" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="ordered">발주대기</option>
              <option value="partial">부분입고</option>
              <option value="received">입고완료</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">물류센터</label>
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
                <th class="cursor-pointer" @click="toggleSort('poId')">발주번호 <i :class="sortIcon('poId')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('product_name')">품목명 <i :class="sortIcon('product_name')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('supplier_name')">공급업체 <i :class="sortIcon('supplier_name')"></i></th>
                <th class="text-end">수량</th>
                <th class="text-end cursor-pointer" @click="toggleSort('linetotal')">발주금액 <i :class="sortIcon('linetotal')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('expecteddate')">납기일 <i :class="sortIcon('expecteddate')"></i></th>
                <th>물류센터</th>
                <th>상태</th>
                <th>처리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pagedRows" :key="row.detailId">
                <td class="small text-muted">{{ row.poCode }}</td>
                <td class="small fw-semibold">
                  <span v-if="isOverdue(row)" class="badge bg-danger-subtle text-danger border border-danger-subtle me-1">지연</span>
                  {{ row.product_name }}
                </td>
                <td class="small">{{ row.supplier_name }}</td>
                <td class="small text-end">{{ row.quantity?.toLocaleString('ko-KR') }}</td>
                <td class="small text-end fw-semibold">{{ fmtMoney(row.linetotal) }}</td>
                <td class="small" :class="isOverdue(row) ? 'text-danger fw-semibold' : 'text-muted'">{{ fmtDate(row.expecteddate) }}</td>
                <td><span class="badge bg-light text-dark border">{{ row.warehouse || '-' }}</span></td>
                <td><span class="badge" :class="statusMeta(row.status).cls">{{ statusMeta(row.status).label }}</span></td>
                <td>
                  <div class="d-flex gap-1">
                    <button v-if="row.status !== 'received'" class="btn btn-xs btn-outline-success" @click="markReceived(row.poId)">입고처리</button>
                    <button class="btn btn-xs btn-outline-secondary" @click="viewDetail(row.poId)">상세</button>
                    <button class="btn btn-xs btn-outline-danger" @click="deletePO(row.poId)">삭제</button>
                  </div>
                </td>
              </tr>
              <tr v-if="pagedRows.length === 0">
                <td colspan="9" class="text-center text-muted small py-4">조건에 맞는 발주 내역이 없습니다</td>
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

    <!-- 발주 등록 모달 -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-backdrop-custom" @click.self="showCreateModal = false">
        <div class="modal-panel shadow-lg" style="width:560px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-file-earmark-plus me-2 text-primary"></i>발주등록</span>
            <button class="btn-close-panel" @click="showCreateModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">공급업체 <span class="text-danger">*</span></label>
                <select v-model="form.supplierid" class="form-select form-select-sm">
                  <option value="">선택</option>
                  <option v-for="s in suppliers" :key="s.supplierid" :value="s.supplierid">{{ s.companyname }}</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">물류센터</label>
                <select v-model="form.warehouse" class="form-select form-select-sm">
                  <option v-for="w in warehouseOptions" :key="w" :value="w">{{ w }}</option>
                </select>
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">발주일</label>
                <input v-model="form.orderdate" type="date" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">납기예정일</label>
                <input v-model="form.expecteddate" type="date" class="form-control form-control-sm" />
              </div>
            </div>

            <label class="form-label small fw-semibold">발주 품목 <span class="text-danger">*</span></label>
            <div v-for="(item, idx) in form.items" :key="idx" class="row g-2 mb-2 align-items-end">
              <div class="col-5">
                <select v-model="item.productid" class="form-select form-select-sm" @change="onProductChange(idx)">
                  <option value="">품목 선택</option>
                  <option v-for="p in products" :key="p.productid" :value="p.productid">{{ p.productname }}</option>
                </select>
              </div>
              <div class="col-2">
                <input v-model.number="item.quantity" type="number" min="1" class="form-control form-control-sm" placeholder="수량" />
              </div>
              <div class="col-2">
                <input v-model.number="item.unitcost" type="number" min="0" step="0.01" class="form-control form-control-sm" placeholder="단가" />
              </div>
              <div class="col-2">
                <input v-model.number="item.discountPct" type="number" min="0" max="100" class="form-control form-control-sm" placeholder="할인%" />
              </div>
              <div class="col-1">
                <button class="btn btn-sm btn-outline-danger w-100" :disabled="form.items.length === 1" @click="removeItemRow(idx)"><i class="bi bi-dash"></i></button>
              </div>
            </div>
            <button class="btn btn-sm btn-outline-primary mb-3" @click="addItemRow"><i class="bi bi-plus-lg me-1"></i>품목 추가</button>

            <div class="d-flex justify-content-between border-top pt-2">
              <span class="small text-muted">예상 발주금액</span>
              <span class="fw-bold">{{ fmtMoney(itemsTotal) }}</span>
            </div>

            <div v-if="createError" class="alert alert-danger small py-2 mt-3 mb-0">{{ createError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showCreateModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="creating" @click="submitCreate">
              <span v-if="creating" class="spinner-border spinner-border-sm me-1"></span>등록
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 발주 상세 모달 -->
    <Teleport to="body">
      <div v-if="selectedPo" class="modal-backdrop-custom" @click.self="selectedPo = null">
        <div class="modal-panel shadow-lg" style="width:520px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-receipt me-2 text-primary"></i>PO-{{ String(selectedPo.id).padStart(6, '0') }} 상세</span>
            <button class="btn-close-panel" @click="selectedPo = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="row small mb-3">
              <div class="col-6 mb-2"><span class="text-muted">공급업체</span><div class="fw-semibold">{{ selectedPo.supplier_name }}</div></div>
              <div class="col-6 mb-2"><span class="text-muted">물류센터</span><div class="fw-semibold">{{ selectedPo.warehouse || '-' }}</div></div>
              <div class="col-6 mb-2"><span class="text-muted">발주일</span><div>{{ fmtDate(selectedPo.orderdate) }}</div></div>
              <div class="col-6 mb-2"><span class="text-muted">납기예정일</span><div>{{ fmtDate(selectedPo.expecteddate) }}</div></div>
              <div class="col-6 mb-2"><span class="text-muted">입고일</span><div>{{ fmtDate(selectedPo.receiveddate) }}</div></div>
              <div class="col-6 mb-2"><span class="text-muted">상태</span><div><span class="badge" :class="statusMeta(selectedPo.status).cls">{{ statusMeta(selectedPo.status).label }}</span></div></div>
            </div>
            <table class="table table-sm">
              <thead class="table-light"><tr><th>품목</th><th class="text-end">수량</th><th class="text-end">단가</th><th class="text-end">금액</th></tr></thead>
              <tbody>
                <tr v-for="d in selectedPo.details" :key="d.id">
                  <td class="small">{{ d.product_name }}</td>
                  <td class="small text-end">{{ d.quantity }}</td>
                  <td class="small text-end">{{ fmtMoney(d.unitcost) }}</td>
                  <td class="small text-end fw-semibold">{{ fmtMoney(d.linetotal) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="text-end small text-muted">운송비</td>
                  <td class="text-end small">{{ fmtMoney(selectedPo.freight) }}</td>
                </tr>
                <tr>
                  <td colspan="3" class="text-end fw-bold">발주 총액</td>
                  <td class="text-end fw-bold">{{ fmtMoney(selectedPo.totalamount) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="modal-panel-footer">
            <button class="btn btn-sm btn-outline-secondary w-100" @click="selectedPo = null">닫기</button>
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
const sortKey = ref('poId')
const sortDir = ref('desc')
const currentPage = ref(1)
const pageSize = 15

const suppliers = ref([])
const products = ref([])

// ── "이번달" 기준: 데이터상 가장 최근 orderdate가 속한 달 ──
// 실데이터가 2023-09 이후로는 없어 실제 캘린더상 이번달로 필터링하면 0건이 되므로,
// 데이터셋의 최신 발주월을 "이번달"의 기준으로 사용한다.
const latestMonth = computed(() => {
  let max = null
  for (const po of store.purchaseOrders) {
    if (po.orderdate && (!max || po.orderdate > max)) max = po.orderdate
  }
  return max ? max.slice(0, 7) : null // 'YYYY-MM'
})
const latestMonthLabel = computed(() => {
  if (!latestMonth.value) return ''
  const [y, m] = latestMonth.value.split('-')
  return `${y}년 ${Number(m)}월`
})
const monthPos = computed(() => {
  if (!latestMonth.value) return []
  return store.purchaseOrders.filter((po) => (po.orderdate || '').startsWith(latestMonth.value))
})

// ── 목록 구성: 이번달 발주 헤더(PurchaseOrder) + 라인아이템(PurchaseOrderDetail)을 한 행으로 펼침 ──
const rows = computed(() => {
  const list = []
  for (const po of monthPos.value) {
    for (const d of po.details || []) {
      list.push({
        poId: po.id,
        poCode: `PO-${String(po.id).padStart(6, '0')}`,
        detailId: d.id,
        product_name: d.product_name,
        quantity: d.quantity,
        linetotal: Number(d.linetotal),
        supplier_name: po.supplier_name,
        orderdate: po.orderdate,
        expecteddate: po.expecteddate,
        receiveddate: po.receiveddate,
        status: po.status,
        warehouse: po.warehouse,
      })
    }
  }
  return list
})

const filteredRows = computed(() => {
  let list = rows.value
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(
      (r) =>
        (r.product_name || '').toLowerCase().includes(q) ||
        (r.poCode || '').toLowerCase().includes(q) ||
        (r.supplier_name || '').toLowerCase().includes(q),
    )
  }
  if (statusFilter.value) list = list.filter((r) => r.status === statusFilter.value)
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
  const pos = monthPos.value
  return {
    total: pos.length,
    pending: pos.filter((p) => p.status === 'ordered').length,
    overdue: pos.filter((p) => p.status !== 'received' && p.expecteddate && new Date(p.expecteddate) < new Date()).length,
    totalAmount: pos.reduce((sum, p) => sum + Number(p.totalamount || 0), 0),
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

function isOverdue(row) {
  return row.status !== 'received' && row.expecteddate && new Date(row.expecteddate) < new Date()
}

function statusMeta(status) {
  const map = {
    ordered: { label: '발주대기', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    partial: { label: '부분입고', cls: 'bg-info-subtle text-info border border-info-subtle' },
    received: { label: '입고완료', cls: 'bg-success-subtle text-success border border-success-subtle' },
  }
  return map[status] || { label: status || '-', cls: 'bg-secondary-subtle text-secondary' }
}

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}
function fmtMoney(v) {
  return '₩' + Math.round(Number(v) || 0).toLocaleString('ko-KR')
}
function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

// ── 입고처리 / 상세 / 삭제 ──
async function markReceived(poId) {
  const po = store.purchaseOrders.find((p) => p.id === poId)
  if (!po) return
  if (!confirm(`PO-${String(poId).padStart(6, '0')} 을 입고완료로 처리하시겠습니까?`)) return
  try {
    await procurementApi.updatePurchaseOrder(poId, {
      supplierid: po.supplierid,
      employeeid: po.employeeid,
      orderdate: po.orderdate,
      expecteddate: po.expecteddate,
      receiveddate: todayStr(),
      status: 'received',
      currency: po.currency,
      freight: po.freight,
      totalamount: po.totalamount,
      warehouse: po.warehouse,
    })
    await store.fetchAll()
  } catch {
    alert('입고처리에 실패했습니다.')
  }
}

function viewDetail(poId) {
  selectedPo.value = store.purchaseOrders.find((p) => p.id === poId) || null
}

async function deletePO(poId) {
  if (!confirm(`PO-${String(poId).padStart(6, '0')} 발주를 삭제하시겠습니까? 하위 품목 내역도 함께 삭제됩니다.`)) return
  try {
    await procurementApi.deletePurchaseOrder(poId)
    await store.fetchAll()
  } catch {
    alert('삭제에 실패했습니다.')
  }
}

const selectedPo = ref(null)

// ── 발주등록 모달 ──
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')

function emptyItem() {
  return { productid: '', quantity: 1, unitcost: 0, discountPct: 0 }
}

const form = reactive({
  supplierid: '',
  warehouse: warehouseOptions[0],
  orderdate: todayStr(),
  expecteddate: '',
  items: [emptyItem()],
})

const itemsTotal = computed(() =>
  form.items.reduce((sum, it) => {
    const qty = Number(it.quantity) || 0
    const cost = Number(it.unitcost) || 0
    const discFrac = (Number(it.discountPct) || 0) / 100
    return sum + qty * cost * (1 - discFrac)
  }, 0),
)

function openCreateModal() {
  form.supplierid = ''
  form.warehouse = warehouseOptions[0]
  form.orderdate = todayStr()
  form.expecteddate = ''
  form.items = [emptyItem()]
  createError.value = ''
  showCreateModal.value = true
}

function addItemRow() {
  form.items.push(emptyItem())
}
function removeItemRow(idx) {
  if (form.items.length > 1) form.items.splice(idx, 1)
}
function onProductChange(idx) {
  const p = products.value.find((x) => x.productid === form.items[idx].productid)
  if (p) form.items[idx].unitcost = Number(p.unitprice) || 0
}

async function submitCreate() {
  if (!form.supplierid) {
    createError.value = '공급업체를 선택하세요.'
    return
  }
  const validItems = form.items.filter((it) => it.productid && Number(it.quantity) > 0)
  if (validItems.length === 0) {
    createError.value = '발주 품목을 1개 이상 입력하세요.'
    return
  }
  creating.value = true
  createError.value = ''
  try {
    const headerRes = await procurementApi.createPurchaseOrder({
      supplierid: form.supplierid,
      orderdate: form.orderdate,
      expecteddate: form.expecteddate || null,
      status: 'ordered',
      currency: 'KRW',
      freight: 0,
      totalamount: Number(itemsTotal.value.toFixed(2)),
      warehouse: form.warehouse,
    })
    const poId = headerRes.data.id
    for (const it of validItems) {
      const qty = Number(it.quantity)
      const cost = Number(it.unitcost) || 0
      const discFrac = (Number(it.discountPct) || 0) / 100
      await procurementApi.createPurchaseOrderDetail({
        purchaseorderid: poId,
        productid: it.productid,
        quantity: qty,
        unitcost: cost,
        discount: discFrac,
        linetotal: Number((qty * cost * (1 - discFrac)).toFixed(2)),
      })
    }
    showCreateModal.value = false
    await store.fetchAll()
  } catch (e) {
    createError.value = e?.response?.data ? JSON.stringify(e.response.data) : '발주 등록에 실패했습니다.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  store.fetchAll()
  const [supRes, prodRes] = await Promise.all([ssafyApi.suppliers(), ssafyApi.products()])
  suppliers.value = supRes.data
  products.value = prodRes.data
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
.btn-xs { padding: 2px 8px; font-size: 0.72rem; border-radius: 6px; }

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
