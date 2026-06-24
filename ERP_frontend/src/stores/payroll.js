import { defineStore } from 'pinia'
import { ref } from 'vue'
import { payrollApi } from '@/api/payroll'

export const usePayrollStore = defineStore('payroll', () => {
  const salaries = ref([])
  const bonuses = ref([])
  const yearEndSettlements = ref([])
  const severances = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [s, b, y, sv] = await Promise.all([
        payrollApi.salaries(),
        payrollApi.bonuses(),
        payrollApi.yearEndSettlements(),
        payrollApi.severances(),
      ])
      salaries.value = s.data
      bonuses.value = b.data
      yearEndSettlements.value = y.data
      severances.value = sv.data
    } finally {
      loading.value = false
    }
  }

  return { salaries, bonuses, yearEndSettlements, severances, loading, fetchAll }
})
