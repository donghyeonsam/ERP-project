<template>
  <div class="auth-page d-flex align-items-center justify-content-center">
    <div class="auth-card card shadow-sm p-4">
      <div class="text-center mb-4">
        <div class="auth-logo mx-auto mb-2">S</div>
        <h5 class="fw-bold mb-0">SSAFY_International</h5>
        <p class="text-muted small mt-1">ERP 시스템 로그인</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label small fw-semibold">아이디</label>
          <input
            v-model="form.username"
            type="text"
            class="form-control"
            placeholder="사용자 아이디"
            required
            autocomplete="username"
          />
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">비밀번호</label>
          <input
            v-model="form.password"
            type="password"
            class="form-control"
            placeholder="비밀번호"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="errorMsg" class="alert alert-danger py-2 small">{{ errorMsg }}</div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          로그인
        </button>

        <div class="text-center">
          <span class="text-muted small">아직 계정이 없으신가요? </span>
          <RouterLink to="/register" class="small fw-semibold">회원가입 (Sign up)</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    router.push({ name: 'home' })
  } catch {
    errorMsg.value = authStore.error || '로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a2236 0%, #2563eb 100%);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  border: none;
}

.auth-logo {
  width: 48px;
  height: 48px;
  background: #2563eb;
  color: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.4rem;
}
</style>
