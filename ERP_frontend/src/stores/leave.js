import { defineStore } from 'pinia'
import { ref } from 'vue'
import { leaveApi } from '@/api/employees'

export const useLeaveStore = defineStore('leave', () => {
  const requests = ref([])
  const balances = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [r, b] = await Promise.all([leaveApi.list(), leaveApi.balances()])
      requests.value = r.data
      balances.value = b.data
    } finally {
      loading.value = false
    }
  }

  return { requests, balances, loading, fetchAll }
})
