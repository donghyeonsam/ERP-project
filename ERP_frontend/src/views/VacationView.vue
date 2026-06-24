<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-calendar-minus me-2"></i>휴가관리</h5>
        <p class="text-muted small mb-0">직원 휴가신청, 승인 및 잔여 연차를 관리합니다</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openApplyModal">
        <i class="bi bi-plus-lg me-1"></i>휴가 신청
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">휴가 신청</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ stats.total }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">승인 완료</div>
          <div class="fw-bold text-success" style="font-size:1.6rem">{{ stats.approved }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">대기 중</div>
          <div class="fw-bold text-warning" style="font-size:1.6rem">{{ stats.pending }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">이번달 사용일수</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ stats.usedThisMonth }}<span class="small fw-normal text-muted ms-1">일</span></div>
        </div>
      </div>
    </div>

    <!-- 토글 -->
    <div class="d-flex gap-3 mb-3 view-tabs">
      <div class="tab-item" :class="{ active: activeView === 'requests' }" @click="activeView = 'requests'">휴가 신청 현황</div>
      <div class="tab-item" :class="{ active: activeView === 'balance' }" @click="activeView = 'balance'">연차 잔여현황</div>
    </div>

    <!-- 신청 현황 -->
    <div v-if="activeView === 'requests'">
      <div class="card erp-card mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">성명</label>
              <input v-model="draft.name" type="text" class="form-control form-control-sm" placeholder="이름 검색" />
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">부서</label>
              <select v-model="draft.department" class="form-select form-select-sm">
                <option value="">전체</option>
                <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label small text-muted mb-1">상태</label>
              <select v-model="draft.status" class="form-select form-select-sm">
                <option value="">전체</option>
                <option value="대기">대기</option>
                <option value="승인">승인</option>
                <option value="반려">반려</option>
              </select>
            </div>
            <div class="col-md-4 d-flex gap-2">
              <button class="btn btn-sm btn-primary flex-grow-1" @click="applyFilters"><i class="bi bi-search me-1"></i>조회</button>
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="resetFilters"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
      <div v-else class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>신청일</th>
                  <th>성명</th>
                  <th>부서</th>
                  <th>휴가종류</th>
                  <th>시작일</th>
                  <th>종료일</th>
                  <th class="text-end">일수</th>
                  <th>상태</th>
                  <th>처리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredRequests" :key="row.id">
                  <td class="small text-muted">{{ fmtDate(row.applied_at) }}</td>
                  <td class="small fw-semibold">{{ row.employee_name }}</td>
                  <td class="small text-muted">{{ row.department || '-' }}</td>
                  <td class="small">{{ row.leave_type }}</td>
                  <td class="small text-muted">{{ row.start_date }}</td>
                  <td class="small text-muted">{{ row.end_date }}</td>
                  <td class="small text-end">{{ row.days }}</td>
                  <td><span class="badge" :class="statusMeta(row.status).cls">{{ row.status }}</span></td>
                  <td>
                    <div v-if="row.status === '대기' && canApprove" class="d-flex gap-1">
                      <button class="btn btn-xs btn-success" @click="act(row.id, 'approve')">승인</button>
                      <button class="btn btn-xs btn-outline-danger" @click="act(row.id, 'reject')">반려</button>
                    </div>
                    <span v-else class="small text-muted">{{ row.approver_name ? `${row.approver_name} 처리` : '-' }}</span>
                  </td>
                </tr>
                <tr v-if="filteredRequests.length === 0">
                  <td colspan="9" class="text-center text-muted small py-4">조건에 맞는 휴가 신청 내역이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 연차 잔여현황 -->
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>성명</th>
                <th>부서</th>
                <th>직책</th>
                <th class="text-end">총 연차</th>
                <th class="text-end">사용</th>
                <th class="text-end">잔여</th>
                <th>현황</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in store.balances" :key="row.employeeid">
                <td class="small fw-semibold">{{ row.name }}</td>
                <td class="small text-muted">{{ row.department || '-' }}</td>
                <td class="small text-muted">{{ row.title }}</td>
                <td class="small text-end">{{ row.total_days }}일</td>
                <td class="small text-end">{{ row.used_days }}일</td>
                <td class="small text-end fw-semibold">{{ row.remaining_days }}일</td>
                <td style="min-width:120px">
                  <div class="progress" style="height:6px">
                    <div class="progress-bar" :class="row.remaining_days <= 3 ? 'bg-danger' : 'bg-primary'"
                         :style="{ width: (row.used_days / row.total_days * 100) + '%' }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 휴가 신청 모달 -->
    <Teleport to="body">
      <div v-if="showApplyModal" class="modal-backdrop-custom" @click.self="showApplyModal = false">
        <div class="modal-panel shadow-lg" style="width:440px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-calendar-plus me-2 text-primary"></i>휴가 신청</span>
            <button class="btn-close-panel" @click="showApplyModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-3">
              <label class="form-label small fw-semibold">휴가종류</label>
              <select v-model="form.leave_type" class="form-select form-select-sm">
                <option value="연차">연차</option>
                <option value="병가">병가</option>
                <option value="경조사">경조사</option>
                <option value="기타">기타</option>
              </select>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">시작일 <span class="text-danger">*</span></label>
                <input v-model="form.start_date" type="date" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">종료일 <span class="text-danger">*</span></label>
                <input v-model="form.end_date" type="date" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">신청 사유</label>
              <input v-model="form.reason" type="text" class="form-control form-control-sm" placeholder="사유를 입력하세요" />
            </div>
            <div v-if="formError" class="alert alert-danger small py-2 mb-0">{{ formError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showApplyModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="saving" @click="submitApply">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>신청
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useLeaveStore } from '@/stores/leave'
import { useAuthStore } from '@/stores/auth'
import { leaveApi } from '@/api/employees'

const store = useLeaveStore()
const authStore = useAuthStore()

const canApprove = computed(() => (authStore.user?.level || 0) >= 4)

const activeView = ref('requests')
const departmentOptions = ['경영지원부', '영업1팀', '영업2팀', '영업3팀']

const draft = reactive({ name: '', department: '', status: '' })
const applied = reactive({ name: '', department: '', status: '' })

function applyFilters() { Object.assign(applied, draft) }
function resetFilters() {
  draft.name = ''; draft.department = ''; draft.status = ''
  applied.name = ''; applied.department = ''; applied.status = ''
}

const filteredRequests = computed(() => {
  let list = store.requests
  if (applied.name) {
    const q = applied.name.toLowerCase()
    list = list.filter((r) => (r.employee_name || '').toLowerCase().includes(q))
  }
  if (applied.department) list = list.filter((r) => r.department === applied.department)
  if (applied.status) list = list.filter((r) => r.status === applied.status)
  return list
})

const stats = computed(() => {
  const list = store.requests
  const now = new Date()
  const usedThisMonth = list
    .filter((r) => r.status === '승인' && new Date(r.start_date).getMonth() === now.getMonth() && new Date(r.start_date).getFullYear() === now.getFullYear())
    .reduce((s, r) => s + Number(r.days), 0)
  return {
    total: list.length,
    approved: list.filter((r) => r.status === '승인').length,
    pending: list.filter((r) => r.status === '대기').length,
    usedThisMonth,
  }
})

function statusMeta(status) {
  const map = {
    '대기': { cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    '승인': { cls: 'bg-success-subtle text-success border border-success-subtle' },
    '반려': { cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
  }
  return map[status] || { cls: 'bg-secondary-subtle text-secondary' }
}

function fmtDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR')
}

async function act(id, action) {
  try {
    if (action === 'approve') await leaveApi.approve(id)
    else await leaveApi.reject(id)
    await store.fetchAll()
  } catch (e) {
    alert(e?.response?.data?.detail || '처리에 실패했습니다.')
  }
}

// ── 휴가 신청 ──
const showApplyModal = ref(false)
const saving = ref(false)
const formError = ref('')
const form = reactive({ leave_type: '연차', start_date: '', end_date: '', reason: '' })

function openApplyModal() {
  form.leave_type = '연차'
  form.start_date = ''
  form.end_date = ''
  form.reason = ''
  formError.value = ''
  showApplyModal.value = true
}

async function submitApply() {
  if (!form.start_date || !form.end_date) {
    formError.value = '시작일과 종료일을 입력하세요.'
    return
  }
  const days = Math.round((new Date(form.end_date) - new Date(form.start_date)) / 86400000) + 1
  if (days <= 0) {
    formError.value = '종료일은 시작일 이후여야 합니다.'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    await leaveApi.create({ ...form, days })
    showApplyModal.value = false
    await store.fetchAll()
  } catch (e) {
    formError.value = e?.response?.data ? JSON.stringify(e.response.data) : '신청에 실패했습니다.'
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
.view-tabs { border-bottom: 1px solid #e5e7eb; }
.tab-item {
  padding: 8px 4px 10px; font-weight: 600; font-size: 0.92rem; color: #94a3b8;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }
.btn-xs { font-size: 0.7rem; padding: 2px 8px; }

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
