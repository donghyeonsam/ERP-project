import { defineStore } from 'pinia'
import { ref } from 'vue'
import { financeApi } from '@/api/finance'

export const useFinanceStore = defineStore('finance', () => {
  const budgets = ref([])
  const expenses = ref([])
  const receivables = ref([])
  const payables = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [b, e, r, p] = await Promise.all([
        financeApi.budgets(),
        financeApi.expenses(),
        financeApi.accountsReceivable(),
        financeApi.accountsPayable(),
      ])
      budgets.value = b.data
      expenses.value = e.data
      receivables.value = r.data
      payables.value = p.data
    } finally {
      loading.value = false
    }
  }

  return { budgets, expenses, receivables, payables, loading, fetchAll }
})
