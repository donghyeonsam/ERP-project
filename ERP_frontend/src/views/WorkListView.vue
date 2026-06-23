<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-kanban me-2"></i>Works</h5>
      <RouterLink to="/works/create" class="btn btn-sm btn-primary">
        <i class="bi bi-plus me-1"></i>새 업무
      </RouterLink>
    </div>

    <div class="card erp-card mb-3">
      <div class="card-body py-2 d-flex gap-2 flex-wrap">
        <select v-model="filterStatus" class="form-select form-select-sm" style="width:auto">
          <option value="">전체 상태</option>
          <option>진행중</option><option>완료</option><option>대기</option><option>지연</option>
        </select>
        <input v-model="search" type="text" class="form-control form-control-sm" placeholder="제목 검색..." style="max-width:200px" />
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else>
      <div v-if="filtered.length === 0" class="text-center text-muted py-5">업무가 없습니다</div>
      <div v-for="task in filtered" :key="task.id" class="card erp-card mb-2 task-card" @click="goDetail(task.id)">
        <div class="card-body py-2 d-flex align-items-center gap-3">
          <span :class="['badge', statusClass(task.status)]">{{ task.status || '진행중' }}</span>
          <div class="flex-grow-1">
            <div class="fw-semibold">{{ task.title }}</div>
            <div class="text-muted small">{{ task.description || '' }}</div>
          </div>
          <div class="text-end">
            <div class="text-muted small">마감: {{ fmtDate(task.due_date) }}</div>
          </div>
          <i class="bi bi-chevron-right text-muted"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useWorksStore } from '@/stores/works'

const router = useRouter()
const worksStore = useWorksStore()
const filterStatus = ref('')
const search = ref('')
const loading = computed(() => worksStore.loading)

const filtered = computed(() => {
  let list = worksStore.tasks
  if (filterStatus.value) list = list.filter(t => t.status === filterStatus.value)
  if (search.value) list = list.filter(t => (t.title||'').toLowerCase().includes(search.value.toLowerCase()))
  return list
})

function statusClass(s) {
  return { '진행중': 'bg-primary', '완료': 'bg-success', '대기': 'bg-secondary', '지연': 'bg-danger' }[s] || 'bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }
function goDetail(id) { router.push(`/works/${id}`) }

onMounted(() => worksStore.fetchTasks())
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.task-card { cursor: pointer; transition: box-shadow 0.15s; }
.task-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>
