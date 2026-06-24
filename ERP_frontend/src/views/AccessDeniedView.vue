<template>
  <div class="d-flex align-items-center justify-content-center" style="min-height: 60vh;">
    <div class="text-center">
      <div class="mb-4 text-secondary" style="font-size: 4.5rem;">
        <i class="bi bi-shield-lock"></i>
      </div>
      <h4 class="fw-bold mb-2">접근 권한이 없습니다</h4>
      <p class="text-muted mb-4">
        이 페이지를 열람할 권한이 없습니다.<br>
        권한이 필요한 경우 관리자에게 문의하세요.
      </p>
      <div class="d-flex gap-2 justify-content-center">
        <button class="btn btn-outline-secondary" @click="$router.back()">
          <i class="bi bi-arrow-left me-1"></i>이전 페이지로
        </button>
        <RouterLink to="/" class="btn btn-primary">
          <i class="bi bi-house me-1"></i>홈으로
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
