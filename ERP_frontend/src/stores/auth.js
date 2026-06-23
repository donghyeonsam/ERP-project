import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref(null)

  async function restoreSession() {
    try {
      const res = await authApi.getMe()
      user.value = res.data
      isAuthenticated.value = true
      return true
    } catch {
      user.value = null
      isAuthenticated.value = false
      return false
    }
  }

  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      await authApi.login(username, password)
      const res = await authApi.getMe()
      user.value = res.data
      isAuthenticated.value = true
    } catch (e) {
      error.value = e.response?.data?.non_field_errors?.[0] || '로그인에 실패했습니다.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {}
    user.value = null
    isAuthenticated.value = false
  }

  async function register(data) {
    loading.value = true
    error.value = null
    try {
      await authApi.register(data)
    } catch (e) {
      const d = e.response?.data
      error.value = Object.values(d || {})[0]?.[0] || '회원가입에 실패했습니다.'
      throw e
    } finally {
      loading.value = false
    }
  }

  return { user, isAuthenticated, loading, error, login, logout, register, restoreSession }
})
