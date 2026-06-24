<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-calendar-check me-2"></i>근태관리</h5>
        <p class="text-muted small mb-0">직원 출퇴근 현황을 조회하고 관리합니다</p>
      </div>
      <button v-if="canManualRegister" class="btn btn-primary btn-sm" @click="openManualModal">
        <i class="bi bi-plus-lg me-1"></i>수동 등록
      </button>
    </div>

    <div class="row g-3 mb-4">
      <!-- 오늘 출퇴근(개인) -->
      <div class="col-md-4">
        <div class="card erp-card text-center p-4">
          <div class="fw-bold" style="font-size:2rem">{{ currentTime }}</div>
          <div class="text-muted small mt-1">{{ todayString }}</div>
          <div class="mt-3 d-flex gap-2 justify-content-center">
            <button
              class="btn btn-sm fw-semibold"
              :class="todayRecord?.checkin_time ? 'btn-success' : 'btn-outline-success'"
              :disabled="!!todayRecord?.checkin_time || saving"
              @click="doCheckIn"
            >
              <i class="bi bi-box-arrow-in-right me-1"></i>
              {{ todayRecord?.checkin_time ? todayRecord.checkin_time.slice(0,5) : '출근' }}
            </button>
            <button
              class="btn btn-sm fw-semibold"
              :class="todayRecord?.checkout_time ? 'btn-secondary' : 'btn-outline-secondary'"
              :disabled="!todayRecord?.checkin_time || saving"
              @click="doCheckOut"
            >
              <i class="bi bi-box-arrow-right me-1"></i>
              {{ todayRecord?.checkout_time ? todayRecord.checkout_time.slice(0,5) + ' ✎' : '퇴근' }}
            </button>
          </div>
          <div class="mt-3">
            <span v-if="todayRecord?.checkin_time && !todayRecord?.checkout_time" class="badge bg-success-subtle text-success border border-success-subtle">근무 중</span>
            <span v-else-if="todayRecord?.checkout_time" class="badge bg-secondary-subtle text-secondary border border-secondary-subtle">퇴근 완료</span>
            <span v-else class="badge bg-warning-subtle text-warning border border-warning-subtle">미출근</span>
          </div>
        </div>
      </div>

      <!-- KPI 카드 -->
      <div class="col-md-8">
        <div class="row g-3 h-100">
          <div class="col-6">
            <div class="card erp-card p-3">
              <div class="text-muted small mb-1">오늘 출근</div>
              <div class="fw-bold" style="font-size:1.4rem">{{ kpi.present }}<span class="small fw-normal text-muted ms-1">명</span></div>
            </div>
          </div>
          <div class="col-6">
            <div class="card erp-card p-3">
              <div class="text-muted small mb-1">지각</div>
              <div class="fw-bold text-warning" style="font-size:1.4rem">{{ kpi.late }}<span class="small fw-normal text-muted ms-1">명</span></div>
            </div>
          </div>
          <div class="col-6">
            <div class="card erp-card p-3">
              <div class="text-muted small mb-1">결근</div>
              <div class="fw-bold text-danger" style="font-size:1.4rem">{{ kpi.absent }}<span class="small fw-normal text-muted ms-1">명</span></div>
            </div>
          </div>
          <div class="col-6">
            <div class="card erp-card p-3">
              <div class="text-muted small mb-1">평균 근무시간</div>
              <div class="fw-bold" style="font-size:1.4rem">{{ kpi.avgHours }}<span class="small fw-normal text-muted ms-1">시간</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 필터 -->
    <div class="card erp-card mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">성명/사번</label>
            <input v-model="draft.name" type="text" class="form-control form-control-sm" placeholder="이름 또는 사번" />
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">부서</label>
            <select v-model="draft.department" class="form-select form-select-sm">
              <option value="">전체</option>
              <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">날짜</label>
            <input v-model="draft.date" type="date" class="form-control form-control-sm" />
          </div>
          <div class="col-md-2">
            <label class="form-label small text-muted mb-1">상태</label>
            <select v-model="draft.status" class="form-select form-select-sm">
              <option value="">전체</option>
              <option value="정상">정상</option>
              <option value="지각">지각</option>
              <option value="조퇴">조퇴</option>
              <option value="결근">결근</option>
              <option value="휴가">휴가</option>
            </select>
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-sm btn-primary flex-grow-1" @click="applyFilters"><i class="bi bi-search me-1"></i>조회</button>
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="resetFilters"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 전사 근태 테이블 -->
    <div v-if="loadingAdmin" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>날짜</th><th>사번</th><th>성명</th><th>부서</th>
                <th>출근시간</th><th>퇴근시간</th><th>근무시간</th><th>상태</th><th>비고</th>
                <th v-if="canManualRegister">관리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rec in filteredAdminRows" :key="rec.id">
                <td class="small text-muted">{{ rec.date }}</td>
                <td class="small text-muted">{{ rec.employee }}</td>
                <td class="small fw-semibold">{{ rec.employee_name }}</td>
                <td class="small text-muted">{{ rec.department || '-' }}</td>
                <td class="small">{{ rec.checkin_time?.slice(0,5) || '--:--' }}</td>
                <td class="small">{{ rec.checkout_time?.slice(0,5) || '--:--' }}</td>
                <td class="small">{{ workHours(rec) }}</td>
                <td><span class="badge" :class="statusBadge(rec.status)">{{ rec.status }}</span></td>
                <td class="small text-muted">{{ rec.note || '' }}</td>
                <td v-if="canManualRegister">
                  <button class="btn-icon" title="수정" @click="openManualModal(rec)"><i class="bi bi-pencil"></i></button>
                </td>
              </tr>
              <tr v-if="filteredAdminRows.length === 0">
                <td colspan="10" class="text-center text-muted small py-4">조건에 맞는 근태 내역이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 수동 등록 모달 -->
    <Teleport to="body">
      <div v-if="showManualModal" class="modal-backdrop-custom" @click.self="showManualModal = false">
        <div class="modal-panel shadow-lg" style="width:440px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-pencil-square me-2 text-primary"></i>근태 수동 등록</span>
            <button class="btn-close-panel" @click="showManualModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">직원 <span class="text-danger">*</span></label>
              <select v-model="manualForm.employee" class="form-select form-select-sm">
                <option value="">선택</option>
                <option v-for="e in employeeStore.employees" :key="e.employeeid" :value="e.employeeid">
                  {{ e.lastname }}{{ e.firstname }} ({{ e.department || '-' }})
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">날짜 <span class="text-danger">*</span></label>
              <input v-model="manualForm.date" type="date" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">출근시간</label>
                <input v-model="manualForm.checkin_time" type="time" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">퇴근시간</label>
                <input v-model="manualForm.checkout_time" type="time" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">상태</label>
              <select v-model="manualForm.status" class="form-select form-select-sm">
                <option value="정상">정상</option>
                <option value="지각">지각</option>
                <option value="조퇴">조퇴</option>
                <option value="결근">결근</option>
                <option value="휴가">휴가</option>
              </select>
            </div>
            <div class="mb-1">
              <label class="form-label small fw-semibold">비고</label>
              <input v-model="manualForm.note" type="text" class="form-control form-control-sm" />
            </div>
            <div v-if="manualError" class="alert alert-danger small py-2 mt-3 mb-0">{{ manualError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showManualModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="manualSaving" @click="submitManual">
              <span v-if="manualSaving" class="spinner-border spinner-border-sm me-1"></span>저장
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { attendanceApi } from '@/api/employees'
import { useAuthStore } from '@/stores/auth'
import { useEmployeeStore } from '@/stores/employees'

const authStore = useAuthStore()
const employeeStore = useEmployeeStore()
const canManualRegister = computed(() => (authStore.user?.level || 0) >= 4)
const departmentOptions = ['경영지원부', '영업1팀', '영업2팀', '영업3팀']

const currentTime = ref('')
const todayString = ref('')
let timer = null

const todayRecord = ref(null)
const saving = ref(false)

function updateClock() {
  const n = new Date()
  currentTime.value = n.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  todayString.value = n.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
}

async function loadToday() {
  try {
    const res = await attendanceApi.today()
    todayRecord.value = res.data
  } catch {
    todayRecord.value = null
  }
}

async function doCheckIn() {
  if (saving.value || todayRecord.value?.checkin_time) return
  saving.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkin(time)
    todayRecord.value = res.data
    await loadAdmin()
  } catch (e) {
    alert(String(e?.response?.data?.detail || e?.response?.data || '출근 처리에 실패했습니다.'))
  } finally {
    saving.value = false
  }
}

async function doCheckOut() {
  if (saving.value || !todayRecord.value?.checkin_time) return
  saving.value = true
  try {
    const time = new Date().toTimeString().slice(0, 8)
    const res = await attendanceApi.checkout(time)
    todayRecord.value = res.data
    await loadAdmin()
  } catch (e) {
    alert(String(e?.response?.data?.detail || e?.response?.data || '퇴근 처리에 실패했습니다.'))
  } finally {
    saving.value = false
  }
}

function workHours(rec) {
  if (!rec?.checkin_time || !rec?.checkout_time) return '-- h'
  try {
    const [ih, im] = rec.checkin_time.split(':').map(Number)
    const [oh, om] = rec.checkout_time.split(':').map(Number)
    const diff = (oh * 60 + om) - (ih * 60 + im)
    if (diff <= 0) return '-- h'
    return `${Math.floor(diff / 60)}h ${diff % 60}m`
  } catch { return '-- h' }
}
function workHoursDecimal(rec) {
  if (!rec?.checkin_time || !rec?.checkout_time) return null
  const [ih, im] = rec.checkin_time.split(':').map(Number)
  const [oh, om] = rec.checkout_time.split(':').map(Number)
  const diff = (oh * 60 + om) - (ih * 60 + im)
  return diff > 0 ? diff / 60 : null
}

function statusBadge(status) {
  const map = { '정상': 'bg-success-subtle text-success', '지각': 'bg-warning-subtle text-warning', '조퇴': 'bg-info-subtle text-info', '결근': 'bg-danger-subtle text-danger', '휴가': 'bg-primary-subtle text-primary' }
  return map[status] || 'bg-secondary-subtle text-secondary'
}

// ── 전사 근태(관리자 뷰) ──
const adminRows = ref([])
const loadingAdmin = ref(false)
const draft = reactive({ name: '', department: '', date: '', status: '' })
const applied = reactive({ name: '', department: '', date: '', status: '' })

async function loadAdmin() {
  loadingAdmin.value = true
  try {
    const res = await attendanceApi.adminList()
    adminRows.value = res.data
  } finally {
    loadingAdmin.value = false
  }
}

const filteredAdminRows = computed(() => {
  let list = adminRows.value
  if (applied.name) {
    const q = applied.name.toLowerCase()
    list = list.filter((r) => (r.employee_name || '').toLowerCase().includes(q) || String(r.employee).includes(q))
  }
  if (applied.department) list = list.filter((r) => r.department === applied.department)
  if (applied.date) list = list.filter((r) => r.date === applied.date)
  if (applied.status) list = list.filter((r) => r.status === applied.status)
  return list
})

function applyFilters() { Object.assign(applied, draft) }
function resetFilters() {
  draft.name = ''; draft.department = ''; draft.date = ''; draft.status = ''
  applied.name = ''; applied.department = ''; applied.date = ''; applied.status = ''
}

const kpi = computed(() => {
  const todayStr = new Date().toISOString().slice(0, 10)
  const todays = adminRows.value.filter((r) => r.date === todayStr)
  const hoursList = todays.map(workHoursDecimal).filter((h) => h != null)
  const avg = hoursList.length ? hoursList.reduce((s, h) => s + h, 0) / hoursList.length : 0
  return {
    present: todays.filter((r) => r.checkin_time).length,
    late: todays.filter((r) => r.status === '지각').length,
    absent: todays.filter((r) => r.status === '결근').length,
    avgHours: avg.toFixed(1),
  }
})

// ── 수동 등록 ──
const showManualModal = ref(false)
const manualSaving = ref(false)
const manualError = ref('')
const manualForm = reactive({ employee: '', date: '', checkin_time: '', checkout_time: '', status: '정상', note: '' })

function openManualModal(rec) {
  manualError.value = ''
  if (rec?.id) {
    manualForm.employee = rec.employee
    manualForm.date = rec.date
    manualForm.checkin_time = rec.checkin_time?.slice(0, 5) || ''
    manualForm.checkout_time = rec.checkout_time?.slice(0, 5) || ''
    manualForm.status = rec.status
    manualForm.note = rec.note || ''
  } else {
    manualForm.employee = ''
    manualForm.date = new Date().toISOString().slice(0, 10)
    manualForm.checkin_time = ''
    manualForm.checkout_time = ''
    manualForm.status = '정상'
    manualForm.note = ''
  }
  showManualModal.value = true
}

async function submitManual() {
  if (!manualForm.employee || !manualForm.date) {
    manualError.value = '직원과 날짜를 입력하세요.'
    return
  }
  manualSaving.value = true
  manualError.value = ''
  try {
    await attendanceApi.manualCreate({ ...manualForm })
    showManualModal.value = false
    await loadAdmin()
  } catch (e) {
    manualError.value = e?.response?.data?.detail || (e?.response?.data ? JSON.stringify(e.response.data) : '저장에 실패했습니다.')
  } finally {
    manualSaving.value = false
  }
}

onMounted(() => {
  updateClock()
  timer = setInterval(updateClock, 1000)
  loadToday()
  loadAdmin()
  employeeStore.fetchAll()
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
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
