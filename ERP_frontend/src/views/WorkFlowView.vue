<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-kanban me-2"></i>워크플로우</h5>
      <RouterLink to="/works/create" class="btn btn-sm btn-primary"><i class="bi bi-plus me-1"></i>새 업무</RouterLink>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="kanban-board">
      <div v-for="col in columns" :key="col.status" class="kanban-col">
        <div class="kanban-col-header mb-2">
          <span class="fw-semibold small">{{ col.label }}</span>
          <span class="badge bg-secondary ms-2">{{ col.tasks.length }}</span>
        </div>
        <div class="kanban-body">
          <div v-for="task in col.tasks" :key="task.id" class="kanban-card card mb-2" @click="router.push(`/works/${task.id}`)">
            <div class="card-body py-2 px-3">
              <div class="fw-semibold small mb-1">{{ task.title }}</div>
              <div class="text-muted" style="font-size:0.72rem">마감: {{ fmtDate(task.due_date) }}</div>
            </div>
          </div>
          <div v-if="col.tasks.length === 0" class="text-muted small text-center py-3">없음</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useWorksStore } from '@/stores/works'

const router = useRouter()
const worksStore = useWorksStore()
const loading = computed(() => worksStore.loading)

const statuses = [
  { status: '대기', label: '대기' },
  { status: '진행중', label: '진행중' },
  { status: '완료', label: '완료' },
  { status: '지연', label: '지연' },
]

const columns = computed(() =>
  statuses.map(s => ({
    ...s,
    tasks: worksStore.tasks.filter(t => (t.status || '진행중') === s.status),
  })),
)

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

onMounted(() => worksStore.fetchTasks())
</script>

<style scoped>
.kanban-board { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 8px; }
.kanban-col { flex: 0 0 250px; background: #f8fafc; border-radius: 12px; padding: 12px; border: 1px solid #e5e7eb; }
.kanban-col-header { display: flex; align-items: center; }
.kanban-body { min-height: 200px; }
.kanban-card { cursor: pointer; border: 1px solid #e5e7eb; border-radius: 8px; transition: box-shadow 0.15s; }
.kanban-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>
