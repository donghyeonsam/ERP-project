import { defineStore } from 'pinia'
import { ref } from 'vue'
import { logisticsApi } from '@/api/logistics'

export const useLogisticsStore = defineStore('logistics', () => {
  const vehicles = ref([])
  const dispatches = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [veh, dis] = await Promise.all([
        logisticsApi.vehicles(),
        logisticsApi.dispatches(),
      ])
      vehicles.value = veh.data
      dispatches.value = dis.data
    } finally {
      loading.value = false
    }
  }

  return { vehicles, dispatches, loading, fetchAll }
})
