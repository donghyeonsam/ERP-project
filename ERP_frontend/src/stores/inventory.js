import { defineStore } from 'pinia'
import { ref } from 'vue'
import { inventoryApi } from '@/api/inventory'

export const useInventoryStore = defineStore('inventory', () => {
  const countPlans = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const res = await inventoryApi.countPlans()
      countPlans.value = res.data
    } finally {
      loading.value = false
    }
  }

  return { countPlans, loading, fetchAll }
})
