import { defineStore } from 'pinia'
import { ref } from 'vue'
import { employeesApi } from '@/api/employees'

export const useEmployeeStore = defineStore('employee', () => {
  const employees = ref([])
  const current = ref(null)
  const orgChart = ref(null)
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const res = await employeesApi.list()
      employees.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const res = await employeesApi.get(id)
      current.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchOrgChart() {
    const res = await employeesApi.orgChart()
    orgChart.value = res.data
  }

  return { employees, current, orgChart, loading, fetchAll, fetchOne, fetchOrgChart }
})
