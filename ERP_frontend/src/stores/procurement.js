import { defineStore } from 'pinia'
import { ref } from 'vue'
import { procurementApi } from '@/api/procurement'

export const useProcurementStore = defineStore('procurement', () => {
  const purchaseOrders = ref([])
  const materials = ref([])
  const goodsReceipts = ref([])
  const boms = ref([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [po, mat, gr, boms_] = await Promise.all([
        procurementApi.purchaseOrders(),
        procurementApi.materials(),
        procurementApi.goodsReceipts(),
        procurementApi.boms(),
      ])
      purchaseOrders.value = po.data
      materials.value = mat.data
      goodsReceipts.value = gr.data
      boms.value = boms_.data
    } finally {
      loading.value = false
    }
  }

  async function fetchBoms() {
    const res = await procurementApi.boms()
    boms.value = res.data
  }

  return { purchaseOrders, materials, goodsReceipts, boms, loading, fetchAll, fetchBoms }
})
