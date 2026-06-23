<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-0"><i class="bi bi-file-earmark-check me-2"></i>전자결재</h5>
        <p class="text-muted small mb-0">E-Approval</p>
      </div>
      <button class="btn btn-sm btn-primary"><i class="bi bi-plus me-1"></i>결재 기안</button>
    </div>

    <!-- TODO: no backend endpoint for e-approval -->
    <div class="alert alert-info small mb-4">
      <i class="bi bi-info-circle me-1"></i>
      전자결재 API 엔드포인트가 아직 준비되지 않았습니다.
      <!-- TODO: no backend endpoint for e-approval documents -->
    </div>

    <!-- Tab -->
    <ul class="nav nav-tabs mb-3">
      <li v-for="tab in tabs" :key="tab" class="nav-item">
        <button :class="['nav-link', activeTab === tab ? 'active' : '']" @click="activeTab = tab">{{ tab }}</button>
      </li>
    </ul>

    <div class="card erp-card">
      <div class="card-body text-center py-5 text-muted">
        <i class="bi bi-file-earmark-check fs-1 d-block mb-2"></i>
        <div class="fw-semibold">{{ activeTab }} 문서가 없습니다</div>
        <div class="small mt-1">백엔드 연동 후 표시됩니다</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const tabs = ['기안함', '결재대기', '결재완료', '반려']
const activeTab = ref('기안함')
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
</style>
