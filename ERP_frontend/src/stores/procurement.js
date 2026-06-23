import { defineStore } from 'pinia'
import { ref } from 'vue'
import { procurementApi } from '@/api/procurement'

export const useProcurementStore = defineStore('procurement', () => {
  const purchaseOrders = ref([])
  const materials = ref([])
  const goodsReceipts = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [po, mat, gr] = await Promise.all([
        procurementApi.purchaseOrders(),
        procurementApi.materials(),
        procurementApi.goodsReceipts(),
      ])
      purchaseOrders.value = po.data
      materials.value = mat.data
      goodsReceipts.value = gr.data
    } finally {
      loading.value = false
    }
  }

  return { purchaseOrders, materials, goodsReceipts, loading, fetchAll }
})
