<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-journal-text me-2 text-warning"></i>메모</h5>
      <button class="btn btn-sm btn-warning fw-semibold" @click="addMemo">
        <i class="bi bi-plus me-1"></i>메모 추가
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <span class="spinner-border text-warning"></span>
    </div>

    <div v-else class="row g-3">
      <div v-for="(memo, idx) in memos" :key="memo.id || idx" class="col-md-4 col-lg-3">
        <div class="card memo-card h-100">
          <div class="card-body d-flex flex-column">
            <textarea
              v-model="memo.content"
              class="flex-grow-1 border-0 bg-transparent w-100 memo-textarea"
              rows="6"
              placeholder="메모를 입력하세요..."
              @blur="updateMemo(memo)"
            ></textarea>
            <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
              <span class="text-muted" style="font-size:0.7rem">{{ fmtDate(memo.updated_at || memo.date) }}</span>
              <button class="btn btn-sm btn-outline-danger py-0 px-1" style="font-size:0.7rem" @click="deleteMemo(memo, idx)">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="memos.length === 0" class="col-12 text-center text-muted py-5">
        <i class="bi bi-journal-text fs-1 d-block mb-3"></i>
        메모가 없습니다. 상단의 <strong>메모 추가</strong> 버튼을 눌러 작성하세요.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { worksApi } from '@/api/works'

const memos = ref([])
const loading = ref(false)

async function loadMemos() {
  loading.value = true
  try {
    const res = await worksApi.memos()
    memos.value = res.data
  } catch {
    const raw = localStorage.getItem('erp_memos')
    memos.value = raw ? JSON.parse(raw) : []
  } finally {
    loading.value = false
  }
}

async function addMemo() {
  try {
    const res = await worksApi.createMemo('')
    memos.value.unshift(res.data)
  } catch {
    memos.value.unshift({ id: null, content: '', date: new Date().toLocaleDateString('ko-KR') })
  }
}

async function updateMemo(memo) {
  if (!memo.content.trim() && memo.id) {
    await deleteMemo(memo, memos.value.indexOf(memo))
    return
  }
  if (!memo.id) return
  try {
    await worksApi.updateMemo(memo.id, memo.content)
  } catch {}
}

async function deleteMemo(memo, idx) {
  if (memo.id) {
    try { await worksApi.deleteMemo(memo.id) } catch {}
  }
  memos.value.splice(idx, 1)
}

function fmtDate(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString('ko-KR') } catch { return d }
}

onMounted(loadMemos)
</script>

<style scoped>
.memo-card {
  background: #fef9c3;
  border: 1px solid #fde68a;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: box-shadow 0.15s;
}
.memo-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.memo-textarea {
  resize: none;
  font-size: 0.85rem;
  outline: none;
  color: #374151;
  background: transparent;
}
</style>
