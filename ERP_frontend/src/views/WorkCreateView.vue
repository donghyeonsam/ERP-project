<template>
  <div style="max-width:600px">
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-sm btn-outline-secondary" @click="$router.back()"><i class="bi bi-arrow-left"></i></button>
      <h5 class="fw-bold mb-0">새 업무 등록</h5>
    </div>

    <div class="card erp-card">
      <div class="card-body">
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label small fw-semibold">제목 <span class="text-danger">*</span></label>
            <input v-model="form.title" type="text" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">설명</label>
            <textarea v-model="form.description" class="form-control" rows="4"></textarea>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-6">
              <label class="form-label small fw-semibold">상태</label>
              <select v-model="form.status" class="form-select">
                <option>진행중</option><option>대기</option><option>완료</option>
              </select>
            </div>
            <div class="col-6">
              <label class="form-label small fw-semibold">마감일</label>
              <input v-model="form.due_date" type="date" class="form-control" />
            </div>
          </div>
          <div v-if="errorMsg" class="alert alert-danger py-2 small">{{ errorMsg }}</div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>등록
            </button>
            <button type="button" class="btn btn-outline-secondary" @click="$router.back()">취소</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useWorksStore } from '@/stores/works'

const router = useRouter()
const worksStore = useWorksStore()
const loading = ref(false)
const errorMsg = ref('')
const form = ref({ title: '', description: '', status: '진행중', due_date: '' })

async function submit() {
  loading.value = true
  errorMsg.value = ''
  try {
    await worksStore.createTask(form.value)
    router.push('/works')
  } catch (e) {
    errorMsg.value = '업무 등록에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
</style>
