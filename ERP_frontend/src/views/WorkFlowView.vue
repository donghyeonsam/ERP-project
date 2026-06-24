<template>
  <div>
    <!-- 날짜 네비게이션 -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-kanban me-2"></i>워크플로우</h5>
      <div class="d-flex align-items-center gap-2">
        <button class="btn btn-sm btn-outline-secondary" @click="changeDay(-1)"><i class="bi bi-chevron-left"></i></button>
        <input v-model="dateInput" type="date" class="form-control form-control-sm" style="width:160px" @change="onDateChange" />
        <button class="btn btn-sm btn-outline-primary" :disabled="isToday" @click="goToday">오늘</button>
        <button class="btn btn-sm btn-outline-secondary" @click="changeDay(1)"><i class="bi bi-chevron-right"></i></button>
        <RouterLink to="/works/create" class="btn btn-sm btn-primary ms-2"><i class="bi bi-plus me-1"></i>새 업무</RouterLink>
      </div>
    </div>

    <!-- AI 추천 워크플로우 -->
    <div class="card erp-card mb-4">
      <div class="card-header bg-white py-2 d-flex justify-content-between align-items-center">
        <span class="fw-semibold small"><i class="bi bi-stars text-primary me-1"></i>AI 추천 워크플로우</span>
        <button class="btn btn-sm btn-outline-secondary" :disabled="store.loading" @click="refresh(true)">
          <span v-if="store.loading" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-arrow-clockwise me-1"></i>새로고침
        </button>
      </div>
      <div class="card-body">
        <div v-if="store.loading" class="text-center text-muted py-4">
          <span class="spinner-border spinner-border-sm me-2"></span>AI가 오늘의 업무를 분석하고 있습니다...
        </div>
        <div v-else-if="store.error" class="text-center text-muted py-4">
          <i class="bi bi-exclamation-circle d-block fs-3 mb-2 text-warning"></i>
          AI 추천을 사용할 수 없습니다 ({{ store.error }}). 원본 업무 목록은 아래에서 확인하세요.
        </div>
        <div v-else-if="store.recommendation.length === 0" class="text-center text-muted py-4">
          <i class="bi bi-check2-circle d-block fs-3 mb-2"></i>오늘 추천할 업무가 없습니다
        </div>
        <div v-else class="flow-row">
          <template v-for="(item, idx) in store.recommendation" :key="item.id">
            <div class="flow-card" :class="cardClass(item)" @click="openDetail(item)">
              <div class="d-flex justify-content-between align-items-start mb-1">
                <span class="badge" :class="priorityBadge(item.priority)">{{ priorityLabel(item.priority) }}</span>
                <i v-if="item.done" class="bi bi-check-circle-fill text-success"></i>
              </div>
              <div class="flow-card-title" :class="{ 'text-decoration-line-through text-muted': item.done }">{{ item.title }}</div>
              <div class="flow-card-sub text-muted">{{ item.type }} · {{ fmtDeadline(item.deadline) }}</div>
            </div>
            <div v-if="idx < store.recommendation.length - 1" class="flow-arrow"><i class="bi bi-arrow-right"></i></div>
          </template>
        </div>
      </div>
    </div>

    <!-- 오늘 할 일 -->
    <div class="d-flex align-items-center justify-content-between mb-2">
      <span class="fw-semibold small">오늘 할 일 ({{ store.taskList.length }}건)</span>
    </div>
    <div v-if="!store.loading && store.taskList.length === 0" class="card erp-card">
      <div class="card-body text-center text-muted py-4">오늘 할 일이 없습니다</div>
    </div>
    <div v-else class="row g-3">
      <div v-for="item in store.taskList" :key="'list-' + item.id" class="col-md-4 col-lg-3">
        <div class="card erp-card h-100" :class="cardClass(item)" style="cursor:pointer" @click="openDetail(item)">
          <div class="card-body py-2 px-3">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <span class="badge" :class="priorityBadge(item.priority)">{{ priorityLabel(item.priority) }}</span>
              <i v-if="item.done" class="bi bi-check-circle-fill text-success"></i>
            </div>
            <div class="fw-semibold small mb-1" :class="{ 'text-decoration-line-through text-muted': item.done }">{{ item.title }}</div>
            <div class="text-muted" style="font-size:0.72rem">{{ item.type }} · 마감 {{ fmtDeadline(item.deadline) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 상세 패널 -->
    <Teleport to="body">
      <div v-if="selected" class="modal-backdrop-custom" @click.self="selected = null">
        <div class="modal-panel shadow-lg" style="width:440px">
          <div class="modal-panel-header">
            <span class="fw-bold small">{{ selected.title }}</span>
            <button class="btn-close-panel" @click="selected = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="mb-2"><span class="badge" :class="priorityBadge(selected.priority)">{{ priorityLabel(selected.priority) }}</span></div>
            <div class="small text-muted mb-1">유형</div>
            <div class="small mb-3">{{ selected.type }}</div>
            <div class="small text-muted mb-1">상태</div>
            <div class="small mb-3">{{ selected.status }}</div>
            <div class="small text-muted mb-1">마감일</div>
            <div class="small mb-3">{{ fmtDeadline(selected.deadline) }}</div>
            <div class="small text-muted mb-1">설명</div>
            <div class="small mb-3">{{ selected.summary || '-' }}</div>
            <div v-if="selected.ai_reason" class="alert alert-light border small mb-0">
              <i class="bi bi-stars text-primary me-1"></i><strong>AI 추천 이유:</strong> {{ selected.ai_reason }}
            </div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <RouterLink v-if="sourceLink(selected)" :to="sourceLink(selected)" class="btn btn-sm btn-outline-primary flex-grow-1">
              <i class="bi bi-box-arrow-up-right me-1"></i>원본 보기
            </RouterLink>
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="selected = null">닫기</button>
            <button
              v-if="selected.id.startsWith('task:') || selected.id.startsWith('order:') || selected.id.startsWith('purchase_order:')"
              class="btn btn-sm flex-grow-1"
              :class="selected.done ? 'btn-outline-secondary' : 'btn-success'"
              :disabled="completing"
              @click="toggleDone(selected)"
            >
              <span v-if="completing" class="spinner-border spinner-border-sm me-1"></span>
              {{ selected.done ? '완료 취소' : '완료 처리' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()

const dateInput = ref(store.selectedDate)
const isToday = computed(() => dateInput.value === new Date().toISOString().slice(0, 10))

let pollTimer = null

function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => store.pollStatuses(), 30000)
}
function stopPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = null
}

async function refresh(force) {
  await store.fetchRecommendation(dateInput.value, force)
  startPolling()
}

function onDateChange() {
  refresh()
}
function changeDay(delta) {
  const d = new Date(dateInput.value)
  d.setDate(d.getDate() + delta)
  dateInput.value = d.toISOString().slice(0, 10)
  refresh()
}
function goToday() {
  dateInput.value = new Date().toISOString().slice(0, 10)
  refresh()
}

function priorityLabel(p) { return { high: '높음', medium: '보통', low: '낮음' }[p] || '보통' }
function priorityBadge(p) {
  const map = {
    high: 'bg-danger-subtle text-danger border border-danger-subtle',
    medium: 'bg-warning-subtle text-warning border border-warning-subtle',
    low: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
  }
  return map[p] || map.low
}
function cardClass(item) {
  if (item.done) return 'card-done'
  if (item.priority === 'high') return 'card-high'
  if (item.priority === 'medium') return 'card-medium'
  return ''
}
function fmtDeadline(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const selected = ref(null)
const completing = ref(false)

function openDetail(item) {
  selected.value = item
}

function sourceLink(item) {
  const [sourceType, sourceId] = item.id.split(':')
  if (sourceType === 'task') return `/works/${sourceId}`
  if (sourceType === 'calendar') return '/calendar'
  return null
}

async function toggleDone(item) {
  completing.value = true
  try {
    await store.updateTaskStatus(item, !item.done)
    selected.value = { ...item, done: !item.done }
  } catch {
    alert('처리에 실패했습니다.')
  } finally {
    completing.value = false
  }
}

onMounted(() => {
  refresh()
})
onUnmounted(() => stopPolling())
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }

.flow-row { display: flex; align-items: stretch; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.flow-card {
  flex: 0 0 200px; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px;
  cursor: pointer; background: #fff; transition: box-shadow 0.15s;
}
.flow-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.flow-card-title { font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; }
.flow-card-sub { font-size: 0.7rem; }
.flow-arrow { display: flex; align-items: center; color: #cbd5e1; font-size: 1.1rem; flex: 0 0 auto; }

.card-high { background: #fef2f2; border-color: #fecaca; }
.card-medium { background: #fffbeb; border-color: #fde68a; }
.card-done { background: #f8fafc; opacity: 0.7; }

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
