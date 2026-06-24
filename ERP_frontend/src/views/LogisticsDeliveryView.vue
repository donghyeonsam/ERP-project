<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-truck me-2"></i>배차관리</h5>
        <p class="text-muted small mb-0">출고 건에 최적의 차량을 배정하여 배송 효율을 극대화합니다.</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <i class="bi bi-plus-lg me-1"></i>배차 등록
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">금일 배차</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.total }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-primary-subtle text-primary"><i class="bi bi-truck"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">배송중</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.inTransit }}<span class="small fw-normal text-muted ms-1">대</span></div>
            </div>
            <div class="kpi-icon bg-success-subtle text-success"><i class="bi bi-geo-alt"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">미배차 주문</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.waiting }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-warning-subtle text-warning"><i class="bi bi-box-seam"></i></div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small mb-1">배송 완료</div>
              <div class="fw-bold" style="font-size:1.6rem">{{ stats.completed }}<span class="small fw-normal text-muted ms-1">건</span></div>
            </div>
            <div class="kpi-icon bg-info-subtle text-info"><i class="bi bi-check-circle"></i></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="draft.status" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="waiting">대기</option>
              <option value="in_transit">배송중</option>
              <option value="completed">완료</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">배송일</label>
            <input v-model="draft.date" type="date" class="form-control form-control-sm" />
          </div>
          <div class="col-md-3">
            <label class="form-label small text-muted mb-1">기사명</label>
            <input v-model="draft.driver" type="text" class="form-control form-control-sm" placeholder="기사명 검색" />
          </div>
          <div class="col-md-4 d-flex gap-2">
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

    <!-- Tab label -->
    <div class="dispatch-tab mb-2">금일 배차현황</div>

    <!-- Table -->
    <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th class="cursor-pointer" @click="toggleSort('code')">배차번호 <i :class="sortIcon('code')"></i></th>
                <th class="cursor-pointer" @click="toggleSort('vehicle_plate')">차량 <i :class="sortIcon('vehicle_plate')"></i></th>
                <th>기사</th>
                <th>배송 지역</th>
                <th class="text-end cursor-pointer" @click="toggleSort('shipmentcount')">배송 건수 <i :class="sortIcon('shipmentcount')"></i></th>
                <th class="text-end cursor-pointer" @click="toggleSort('totalweightkg')">총 중량 <i :class="sortIcon('totalweightkg')"></i></th>
                <th>적재율</th>
                <th class="cursor-pointer" @click="toggleSort('departuretime')">출발시간 <i :class="sortIcon('departuretime')"></i></th>
                <th>상태</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pagedRows" :key="row.id">
                <td class="small text-muted">{{ row.code }}</td>
                <td class="small">
                  <div class="fw-semibold">{{ row.vehicle_plate }}</div>
                  <div class="text-muted" style="font-size:0.72rem">({{ row.vehicle_capacity_label }})</div>
                </td>
                <td class="small">{{ row.drivername }}</td>
                <td class="small">{{ row.region }}</td>
                <td class="small text-end">{{ row.shipmentcount }}건</td>
                <td class="small text-end">{{ Number(row.totalweightkg).toLocaleString('ko-KR') }} kg</td>
                <td style="min-width:110px">
                  <div class="d-flex align-items-center gap-2">
                    <div class="progress flex-grow-1" style="height:6px">
                      <div class="progress-bar bg-warning" :style="{ width: row.load_rate + '%' }"></div>
                    </div>
                    <span class="small text-muted">{{ row.load_rate }}%</span>
                  </div>
                </td>
                <td class="small text-muted">{{ fmtDateTime(row.departuretime) }}</td>
                <td><span class="badge" :class="statusMeta(row.status).cls">{{ statusMeta(row.status).label }}</span></td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn-icon" title="수정" @click="openEditModal(row)"><i class="bi bi-pencil"></i></button>
                    <button class="btn-icon text-danger" title="삭제" @click="deleteDispatch(row.id)"><i class="bi bi-trash"></i></button>
                  </div>
                </td>
              </tr>
              <tr v-if="pagedRows.length === 0">
                <td colspan="10" class="text-center text-muted small py-4">조건에 맞는 배차 내역이 없습니다</td>
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

    <!-- 배차등록 / 수정 모달 -->
    <Teleport to="body">
      <div v-if="showFormModal" class="modal-backdrop-custom" @click.self="showFormModal = false">
        <div class="modal-panel shadow-lg" style="width:480px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-truck me-2 text-primary"></i>{{ editingId ? '배차 수정' : '배차 등록' }}</span>
            <button class="btn-close-panel" @click="showFormModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">차량 <span class="text-danger">*</span></label>
              <select v-model="form.vehicleid" class="form-select form-select-sm">
                <option value="">선택</option>
                <option v-for="v in store.vehicles" :key="v.id" :value="v.id">
                  {{ v.platenumber }} ({{ v.capacitylabel }})
                </option>
              </select>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">기사명 <span class="text-danger">*</span></label>
                <input v-model="form.drivername" type="text" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">배송 지역 <span class="text-danger">*</span></label>
                <input v-model="form.region" type="text" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">배송 건수</label>
                <input v-model.number="form.shipmentcount" type="number" min="0" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">총 중량(kg)</label>
                <input v-model.number="form.totalweightkg" type="number" min="0" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">배송일</label>
                <input v-model="form.dispatchdate" type="date" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">출발시간</label>
                <input v-model="form.departuretimeOnly" type="time" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-1">
              <label class="form-label small fw-semibold">상태</label>
              <select v-model="form.status" class="form-select form-select-sm">
                <option value="waiting">대기</option>
                <option value="in_transit">배송중</option>
                <option value="completed">완료</option>
              </select>
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
import { useLogisticsStore } from '@/stores/logistics'
import { logisticsApi } from '@/api/logistics'

const store = useLogisticsStore()

const draft = reactive({ status: '', date: '', driver: '' })
const applied = reactive({ status: '', date: '', driver: '' })

const sortKey = ref('departuretime')
const sortDir = ref('asc')
const currentPage = ref(1)
const pageSize = 15

// ── "금일" 기준: 데이터상 가장 최근 dispatchdate ──
const latestDay = computed(() => {
  let max = null
  for (const d of store.dispatches) {
    if (d.dispatchdate && (!max || d.dispatchdate > max)) max = d.dispatchdate
  }
  return max
})

const todaysRows = computed(() => store.dispatches.filter((d) => d.dispatchdate === latestDay.value))

const stats = computed(() => {
  const list = todaysRows.value
  return {
    total: list.length,
    inTransit: list.filter((d) => d.status === 'in_transit').length,
    waiting: list.filter((d) => d.status === 'waiting').length,
    completed: list.filter((d) => d.status === 'completed').length,
  }
})

const filteredRows = computed(() => {
  const targetDate = applied.date || latestDay.value
  let list = store.dispatches.filter((d) => d.dispatchdate === targetDate)
  if (applied.status) list = list.filter((d) => d.status === applied.status)
  if (applied.driver) {
    const q = applied.driver.toLowerCase()
    list = list.filter((d) => (d.drivername || '').toLowerCase().includes(q))
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

watch(() => [applied.status, applied.date, applied.driver], () => {
  currentPage.value = 1
})

function applyFilters() {
  applied.status = draft.status
  applied.date = draft.date
  applied.driver = draft.driver
}

function resetFilters() {
  draft.status = ''
  draft.date = ''
  draft.driver = ''
  applied.status = ''
  applied.date = ''
  applied.driver = ''
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
    waiting: { label: '대기', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    in_transit: { label: '배송중', cls: 'bg-success-subtle text-success border border-success-subtle' },
    completed: { label: '완료', cls: 'bg-primary-subtle text-primary border border-primary-subtle' },
  }
  return map[status] || { label: status || '-', cls: 'bg-secondary-subtle text-secondary' }
}

function fmtDateTime(dt) {
  if (!dt) return '-'
  const d = new Date(dt)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

// ── 배차등록 / 수정 / 삭제 ──
const showFormModal = ref(false)
const saving = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = reactive({
  vehicleid: '',
  drivername: '',
  region: '',
  shipmentcount: 0,
  totalweightkg: 0,
  dispatchdate: todayStr(),
  departuretimeOnly: '09:00',
  status: 'waiting',
})

function openCreateModal() {
  editingId.value = null
  form.vehicleid = ''
  form.drivername = ''
  form.region = ''
  form.shipmentcount = 0
  form.totalweightkg = 0
  form.dispatchdate = todayStr()
  form.departuretimeOnly = '09:00'
  form.status = 'waiting'
  formError.value = ''
  showFormModal.value = true
}

function openEditModal(row) {
  editingId.value = row.id
  form.vehicleid = row.vehicleid
  form.drivername = row.drivername
  form.region = row.region
  form.shipmentcount = row.shipmentcount
  form.totalweightkg = Number(row.totalweightkg)
  form.dispatchdate = row.dispatchdate
  const d = new Date(row.departuretime)
  const pad = (n) => String(n).padStart(2, '0')
  form.departuretimeOnly = `${pad(d.getHours())}:${pad(d.getMinutes())}`
  form.status = row.status
  formError.value = ''
  showFormModal.value = true
}

async function submitForm() {
  if (!form.vehicleid || !form.drivername || !form.region) {
    formError.value = '차량, 기사명, 배송 지역을 입력하세요.'
    return
  }
  saving.value = true
  formError.value = ''
  const payload = {
    vehicleid: form.vehicleid,
    drivername: form.drivername,
    region: form.region,
    shipmentcount: Number(form.shipmentcount) || 0,
    totalweightkg: Number(form.totalweightkg) || 0,
    dispatchdate: form.dispatchdate,
    departuretime: `${form.dispatchdate}T${form.departuretimeOnly}:00`,
    status: form.status,
  }
  try {
    if (editingId.value) {
      await logisticsApi.updateDispatch(editingId.value, payload)
    } else {
      await logisticsApi.createDispatch(payload)
    }
    showFormModal.value = false
    await store.fetchAll()
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.'
  } finally {
    saving.value = false
  }
}

async function deleteDispatch(id) {
  if (!confirm('해당 배차 내역을 삭제하시겠습니까?')) return
  try {
    await logisticsApi.deleteDispatch(id)
    await store.fetchAll()
  } catch {
    alert('삭제에 실패했습니다.')
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

.dispatch-tab {
  display: inline-block;
  font-weight: 600;
  font-size: 0.92rem;
  color: #2563eb;
  padding-bottom: 6px;
  border-bottom: 2px solid #2563eb;
}

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
