<template>
  <div class="auth-page d-flex align-items-center justify-content-center">
    <div class="auth-card card shadow-sm p-4">
      <div class="text-center mb-4">
        <div class="auth-logo mx-auto mb-2">S</div>
        <h5 class="fw-bold mb-0">회원가입</h5>
        <p class="text-muted small mt-1">사원번호로 계정을 생성합니다</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label small fw-semibold">사원번호 <span class="text-danger">*</span></label>
          <input
            v-model.number="form.employeeid"
            type="number"
            class="form-control"
            placeholder="사원번호 입력"
            required
            min="1"
          />
          <div class="form-text">회사에서 부여받은 사원번호를 입력하세요.</div>
        </div>

        <div class="mb-3">
          <label class="form-label small fw-semibold">아이디 <span class="text-danger">*</span></label>
          <input
            v-model="form.username"
            type="text"
            class="form-control"
            placeholder="사용할 아이디"
            required
            autocomplete="username"
          />
        </div>

        <div class="mb-3">
          <label class="form-label small fw-semibold">비밀번호 <span class="text-danger">*</span></label>
          <input
            v-model="form.password1"
            type="password"
            class="form-control"
            placeholder="비밀번호 (8자 이상)"
            required
            autocomplete="new-password"
          />
        </div>

        <div class="mb-3">
          <label class="form-label small fw-semibold">비밀번호 확인 <span class="text-danger">*</span></label>
          <input
            v-model="form.password2"
            type="password"
            class="form-control"
            placeholder="비밀번호 재입력"
            required
            autocomplete="new-password"
          />
        </div>

        <div v-if="errorMsg" class="alert alert-danger py-2 small">{{ errorMsg }}</div>
        <div v-if="successMsg" class="alert alert-success py-2 small">{{ successMsg }}</div>

        <button type="submit" class="btn btn-primary w-100 mb-3" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          가입하기
        </button>

        <div class="text-center">
          <span class="text-muted small">이미 계정이 있으신가요? </span>
          <RouterLink to="/login" class="small fw-semibold">로그인</RouterLink>
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

const form = ref({ employeeid: '', username: '', password1: '', password2: '' })
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''

  if (form.value.password1 !== form.value.password2) {
    errorMsg.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  loading.value = true
  try {
    // TODO: confirm backend exposes /dj-rest-auth/registration/
    await authStore.register({
      employeeid: form.value.employeeid,
      username: form.value.username,
      password1: form.value.password1,
      password2: form.value.password2,
    })
    successMsg.value = '가입이 완료되었습니다. 로그인 페이지로 이동합니다.'
    setTimeout(() => router.push({ name: 'login' }), 1500)
  } catch {
    errorMsg.value = authStore.error || '회원가입에 실패했습니다. 사원번호를 확인해주세요.'
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
  max-width: 420px;
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
