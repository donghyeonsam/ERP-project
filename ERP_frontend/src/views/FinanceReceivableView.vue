<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-receipt-cutoff me-2"></i>채권채무관리</h5>
        <p class="text-muted small mb-0">매출채권, 매입채무 통합 관리 및 연령분석을 확인합니다.</p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">매출채권 총액</div>
              <div class="fw-bold" style="font-size:1.4rem">{{ fmtCurrency(kpi.arOutstanding) }}</div>
            </div>
            <div class="kpi-icon bg-primary-subtle text-primary"><i class="bi bi-cash-coin"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">매입채무 총액</div>
              <div class="fw-bold" style="font-size:1.4rem">{{ fmtCurrency(kpi.apOutstanding) }}</div>
            </div>
            <div class="kpi-icon bg-warning-subtle text-warning"><i class="bi bi-wallet2"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">연체 건수</div>
              <div class="fw-bold text-danger" style="font-size:1.6rem">{{ kpi.overdueCount }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-danger-subtle text-danger"><i class="bi bi-exclamation-triangle"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">연체 금액</div>
              <div class="fw-bold text-danger" style="font-size:1.4rem">{{ fmtCurrency(kpi.overdueAmount) }}</div>
            </div>
            <div class="kpi-icon bg-danger-subtle text-danger"><i class="bi bi-graph-down-arrow"></i></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="d-flex gap-3 mb-3 receivable-tabs">
      <div class="tab-item" :class="{ active: activeTab === 'receivable' }" @click="activeTab = 'receivable'">매출채권</div>
      <div class="tab-item" :class="{ active: activeTab === 'payable' }" @click="activeTab = 'payable'">매입채무</div>
      <div class="tab-item" :class="{ active: activeTab === 'aging' }" @click="activeTab = 'aging'">연령분석</div>
    </div>

    <!-- Filters (receivable / payable tabs only) -->
    <div v-if="activeTab !== 'aging'" class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="draft.status" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="open">정상</option>
              <option value="overdue">연체</option>
              <option value="paid">완납</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label small text-muted mb-1">거래처</label>
            <input v-model="draft.partner" type="text" class="form-control form-control-sm" placeholder="거래처명 검색" />
          </div>
          <div class="col-md-5 d-flex gap-2">
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

    <!-- 매출채권 / 매입채무 테이블 -->
    <div v-if="activeTab !== 'aging'">
      <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
      <div v-else class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th class="cursor-pointer" @click="toggleSort('partnerName')">거래처 <i :class="sortIcon('partnerName')"></i></th>
                  <th>구분</th>
                  <th class="cursor-pointer" @click="toggleSort('occurrenceDate')">발생일 <i :class="sortIcon('occurrenceDate')"></i></th>
                  <th class="cursor-pointer" @click="toggleSort('dueDate')">만기일 <i :class="sortIcon('dueDate')"></i></th>
                  <th class="text-end cursor-pointer" @click="toggleSort('amount')">{{ activeTab === 'receivable' ? '채권액' : '채무액' }} <i :class="sortIcon('amount')"></i></th>
                  <th class="text-end">잔액</th>
                  <th class="text-end cursor-pointer" @click="toggleSort('overdueDays')">연체일수 <i :class="sortIcon('overdueDays')"></i></th>
                  <th>상태</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in pagedRows" :key="row.id">
                  <td class="small fw-semibold">{{ row.partnerName }}</td>
                  <td class="small text-muted">{{ row.partnerType }}</td>
                  <td class="small text-muted">{{ fmtDate(row.occurrenceDate) }}</td>
                  <td class="small text-muted">{{ fmtDate(row.dueDate) }}</td>
                  <td class="small text-end">{{ fmtCurrency(row.amount) }}</td>
                  <td class="small text-end">{{ fmtCurrency(row.balance) }}</td>
                  <td class="small text-end" :class="row.overdueDays > 0 ? 'text-danger fw-semibold' : 'text-muted'">
                    {{ row.overdueDays > 0 ? row.overdueDays + '일' : '-' }}
                  </td>
                  <td><span class="badge" :class="statusMeta(row.status).cls">{{ statusMeta(row.status).label }}</span></td>
                  <td>
                    <div class="d-flex gap-1">
                      <button v-if="row.status === 'overdue'" class="btn-icon text-danger" title="독촉" @click="sendDunning(row)"><i class="bi bi-bell"></i></button>
                      <button class="btn-icon" title="수정" @click="openEditModal(row)"><i class="bi bi-pencil"></i></button>
                    </div>
                  </td>
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

    <!-- 연령분석 탭 -->
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>연령 구간</th>
                <th class="text-end">매출채권 건수</th>
                <th class="text-end">매출채권 금액</th>
                <th class="text-end">매입채무 건수</th>
                <th class="text-end">매입채무 금액</th>
                <th class="text-end">합계 금액</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="bucket in agingBuckets" :key="bucket.label">
                <td class="small fw-semibold">{{ bucket.label }}</td>
                <td class="small text-end">{{ bucket.arCount }}건</td>
                <td class="small text-end">{{ fmtCurrency(bucket.arAmount) }}</td>
                <td class="small text-end">{{ bucket.apCount }}건</td>
                <td class="small text-end">{{ fmtCurrency(bucket.apAmount) }}</td>
                <td class="small text-end fw-semibold">{{ fmtCurrency(bucket.arAmount + bucket.apAmount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="table-light">
                <td class="small fw-bold">합계</td>
                <td class="small text-end fw-bold">{{ agingTotal.arCount }}건</td>
                <td class="small text-end fw-bold">{{ fmtCurrency(agingTotal.arAmount) }}</td>
                <td class="small text-end fw-bold">{{ agingTotal.apCount }}건</td>
                <td class="small text-end fw-bold">{{ fmtCurrency(agingTotal.apAmount) }}</td>
                <td class="small text-end fw-bold">{{ fmtCurrency(agingTotal.arAmount + agingTotal.apAmount) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      <div class="card-footer py-2 bg-white">
        <span class="small text-muted">기준일: {{ fmtDate(anchorDate) }} · 완납 건은 잔액이 없어 분석에서 제외됩니다.</span>
      </div>
    </div>

    <!-- 수정 모달 -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-backdrop-custom" @click.self="showEditModal = false">
        <div class="modal-panel shadow-lg" style="width:440px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-pencil-square me-2 text-primary"></i>{{ editingType === 'receivable' ? '매출채권' : '매입채무' }} 수정</span>
            <button class="btn-close-panel" @click="showEditModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">거래처</label>
              <input :value="editingPartnerName" type="text" class="form-control form-control-sm" disabled />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">발생일</label>
                <input v-model="form.invoicedate" type="date" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">만기일</label>
                <input v-model="form.duedate" type="date" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">금액</label>
                <input v-model.number="form.amount" type="number" min="0" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">결제조건</label>
                <input v-model="form.paymentterms" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-1">
              <label class="form-label small fw-semibold">상태</label>
              <select v-model="form.status" class="form-select form-select-sm">
                <option value="open">정상</option>
                <option value="overdue">연체</option>
                <option value="paid">완납</option>
              </select>
            </div>
            <div v-if="formError" class="alert alert-danger small py-2 mt-3 mb-0">{{ formError }}</div>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useFinanceStore } from '@/stores/finance'
import { financeApi } from '@/api/finance'

const store = useFinanceStore()

const activeTab = ref('receivable')

const draft = reactive({ status: '', partner: '' })
const applied = reactive({ status: '', partner: '' })

const sortKey = ref('dueDate')
const sortDir = ref('desc')
const currentPage = ref(1)
const pageSize = 15

// ── 데이터셋 자체의 최신 만기일을 "기준일"로 사용 (실제 데이터가 과거 시점이라 시스템 날짜 대신 사용) ──
const anchorDate = computed(() => {
  let max = null
  for (const r of store.receivables) if (r.duedate && (!max || r.duedate > max)) max = r.duedate
  for (const p of store.payables) if (p.duedate && (!max || p.duedate > max)) max = p.duedate
  return max
})

function overdueDays(duedate, status) {
  if (status === 'paid' || !anchorDate.value || !duedate) return 0
  const diff = (new Date(anchorDate.value) - new Date(duedate)) / 86400000
  return diff > 0 ? Math.round(diff) : 0
}

const receivableRows = computed(() =>
  store.receivables.map((r) => ({
    id: r.id,
    type: 'receivable',
    partnerName: r.customer_name || r.customerid,
    partnerType: '고객사',
    occurrenceDate: r.invoicedate,
    dueDate: r.duedate,
    amount: Number(r.amount),
    balance: r.status === 'paid' ? 0 : Number(r.amount),
    overdueDays: overdueDays(r.duedate, r.status),
    status: r.status,
    raw: r,
  })),
)

const payableRows = computed(() =>
  store.payables.map((p) => ({
    id: p.id,
    type: 'payable',
    partnerName: p.supplier_name || p.supplierid,
    partnerType: '공급업체',
    occurrenceDate: p.invoicedate,
    dueDate: p.duedate,
    amount: Number(p.amount),
    balance: p.status === 'paid' ? 0 : Number(p.amount),
    overdueDays: overdueDays(p.duedate, p.status),
    status: p.status,
    raw: p,
  })),
)

const kpi = computed(() => {
  const ar = receivableRows.value
  const ap = payableRows.value
  const overdueAll = [...ar, ...ap].filter((r) => r.status === 'overdue')
  return {
    arOutstanding: ar.reduce((sum, r) => sum + r.balance, 0),
    apOutstanding: ap.reduce((sum, r) => sum + r.balance, 0),
    overdueCount: overdueAll.length,
    overdueAmount: overdueAll.reduce((sum, r) => sum + r.amount, 0),
  }
})

const baseRows = computed(() => (activeTab.value === 'payable' ? payableRows.value : receivableRows.value))

const filteredRows = computed(() => {
  let list = baseRows.value
  if (applied.status) list = list.filter((r) => r.status === applied.status)
  if (applied.partner) {
    const q = applied.partner.toLowerCase()
    list = list.filter((r) => (r.partnerName || '').toLowerCase().includes(q))
  }
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

watch(activeTab, () => {
  currentPage.value = 1
  draft.status = ''
  draft.partner = ''
  applied.status = ''
  applied.partner = ''
})
watch(() => [applied.status, applied.partner], () => {
  currentPage.value = 1
})

function applyFilters() {
  applied.status = draft.status
  applied.partner = draft.partner
}
function resetFilters() {
  draft.status = ''
  draft.partner = ''
  applied.status = ''
  applied.partner = ''
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

function statusMeta(status) {
  const map = {
    open: { label: '정상', cls: 'bg-primary-subtle text-primary border border-primary-subtle' },
    overdue: { label: '연체', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    paid: { label: '완납', cls: 'bg-success-subtle text-success border border-success-subtle' },
  }
  return map[status] || { label: status || '-', cls: 'bg-secondary-subtle text-secondary' }
}

function fmtCurrency(v) {
  if (v == null) return '-'
  return Math.round(Number(v)).toLocaleString('ko-KR') + '원'
}
function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}

// ── 연령분석 ──
const AGING_BUCKETS = [
  { label: '0~30일', min: 0, max: 30 },
  { label: '31~60일', min: 31, max: 60 },
  { label: '61~90일', min: 61, max: 90 },
  { label: '90일 초과', min: 91, max: Infinity },
]

const agingBuckets = computed(() =>
  AGING_BUCKETS.map((b) => {
    const arInBucket = receivableRows.value.filter((r) => r.balance > 0 && r.overdueDays >= b.min && r.overdueDays <= b.max)
    const apInBucket = payableRows.value.filter((r) => r.balance > 0 && r.overdueDays >= b.min && r.overdueDays <= b.max)
    return {
      label: b.label,
      arCount: arInBucket.length,
      arAmount: arInBucket.reduce((s, r) => s + r.balance, 0),
      apCount: apInBucket.length,
      apAmount: apInBucket.reduce((s, r) => s + r.balance, 0),
    }
  }),
)
const agingTotal = computed(() =>
  agingBuckets.value.reduce(
    (acc, b) => ({
      arCount: acc.arCount + b.arCount,
      arAmount: acc.arAmount + b.arAmount,
      apCount: acc.apCount + b.apCount,
      apAmount: acc.apAmount + b.apAmount,
    }),
    { arCount: 0, arAmount: 0, apCount: 0, apAmount: 0 },
  ),
)

// ── 독촉 ──
function sendDunning(row) {
  alert(`${row.partnerName} 거래처에 독촉 알림을 발송했습니다.`)
}

// ── 수정 ──
const showEditModal = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)
const editingType = ref('receivable')
const editingPartnerName = ref('')
const editingRaw = ref(null)

const form = reactive({
  invoicedate: '',
  duedate: '',
  amount: 0,
  paymentterms: '',
  status: 'open',
})

function openEditModal(row) {
  editingId.value = row.id
  editingType.value = row.type
  editingPartnerName.value = row.partnerName
  editingRaw.value = row.raw
  form.invoicedate = row.occurrenceDate
  form.duedate = row.dueDate
  form.amount = row.amount
  form.paymentterms = row.raw.paymentterms
  form.status = row.status
  formError.value = ''
  showEditModal.value = true
}

async function submitEdit() {
  saving.value = true
  formError.value = ''
  try {
    if (editingType.value === 'receivable') {
      const payload = {
        orderid: editingRaw.value.orderid,
        customerid: editingRaw.value.customerid,
        invoicedate: form.invoicedate,
        duedate: form.duedate,
        amount: form.amount,
        currency: editingRaw.value.currency,
        paymentterms: form.paymentterms,
        status: form.status,
      }
      await financeApi.updateAccountsReceivable(editingId.value, payload)
    } else {
      const payload = {
        purchaseorderid: editingRaw.value.purchaseorderid,
        supplierid: editingRaw.value.supplierid,
        invoicedate: form.invoicedate,
        duedate: form.duedate,
        amount: form.amount,
        currency: editingRaw.value.currency,
        paymentterms: form.paymentterms,
        status: form.status,
      }
      await financeApi.updateAccountsPayable(editingId.value, payload)
    }
    showEditModal.value = false
    await store.fetchAll()
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.fetchAll()
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

.receivable-tabs { border-bottom: 1px solid #e5e7eb; }
.tab-item {
  padding: 8px 4px 10px; font-weight: 600; font-size: 0.92rem; color: #94a3b8;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }

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
