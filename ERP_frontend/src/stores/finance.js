import { defineStore } from 'pinia'
import { ref } from 'vue'
import { financeApi } from '@/api/finance'

export const useFinanceStore = defineStore('finance', () => {
  const expenses = ref([])
  const receivables = ref([])
  const payables = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [e, r, p] = await Promise.all([
        financeApi.expenses(),
        financeApi.accountsReceivable(),
        financeApi.accountsPayable(),
      ])
      expenses.value = e.data
      receivables.value = r.data
      payables.value = p.data
    } finally {
      loading.value = false
    }
  }

  return { expenses, receivables, payables, loading, fetchAll }
})
