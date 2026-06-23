<template>
  <div>
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-sm btn-outline-secondary" @click="$router.back()"><i class="bi bi-arrow-left"></i></button>
      <h5 class="fw-bold mb-0">업무 상세</h5>
    </div>

    <div v-if="loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else-if="task" class="row g-3">
      <div class="col-md-8">
        <div class="card erp-card mb-3">
          <div class="card-body">
            <div class="d-flex align-items-start justify-content-between mb-3">
              <div>
                <h6 class="fw-bold mb-1">{{ task.title }}</h6>
                <span :class="['badge', statusClass(task.status)]">{{ task.status || '진행중' }}</span>
              </div>
            </div>
            <p class="text-muted">{{ task.description || '설명 없음' }}</p>
            <div class="row g-2 mt-2">
              <div class="col-6">
                <div class="small text-muted mb-1">마감일</div>
                <div class="small fw-semibold">{{ fmtDate(task.due_date) }}</div>
              </div>
              <div class="col-6">
                <div class="small text-muted mb-1">생성일</div>
                <div class="small fw-semibold">{{ fmtDate(task.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments -->
        <div class="card erp-card">
          <div class="card-header py-2"><span class="fw-semibold small"><i class="bi bi-chat-left-text me-1"></i>댓글</span></div>
          <div class="card-body p-2">
            <div v-for="c in comments" :key="c.id" class="comment-item p-2 rounded mb-2">
              <div class="small fw-semibold mb-1">{{ c.author_name || c.author }}</div>
              <div class="small">{{ c.content }}</div>
              <div class="text-muted mt-1" style="font-size:0.7rem">{{ fmtDate(c.created_at) }}</div>
            </div>
            <div v-if="comments.length === 0" class="text-muted small text-center py-2">댓글이 없습니다</div>
          </div>
          <div class="card-footer py-2">
            <div class="d-flex gap-2">
              <input v-model="newComment" type="text" class="form-control form-control-sm" placeholder="댓글 작성..." @keyup.enter="submitComment" />
              <button class="btn btn-sm btn-primary" @click="submitComment">등록</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { worksApi } from '@/api/works'

const route = useRoute()
const task = ref(null)
const comments = ref([])
const loading = ref(false)
const newComment = ref('')

function statusClass(s) {
  return { '진행중': 'bg-primary', '완료': 'bg-success', '대기': 'bg-secondary', '지연': 'bg-danger' }[s] || 'bg-secondary'
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

async function submitComment() {
  if (!newComment.value.trim()) return
  newComment.value = ''
}

onMounted(async () => {
  loading.value = true
  try {
    const [tRes, cRes] = await Promise.all([
      worksApi.tasks().then(r => r.data.find(t => t.id == route.params.id)),
      worksApi.taskComments(route.params.id),
    ])
    task.value = tRes
    comments.value = Array.isArray(cRes.data) ? cRes.data : []
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { background: #fff; border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.erp-card .card-footer { background: #fff; border-top: 1px solid #f1f5f9; }
.comment-item { background: #f8fafc; }
</style>
