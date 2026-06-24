import { defineStore } from 'pinia'
import { ref } from 'vue'
import { worksApi } from '@/api/works'
import { ssafyApi } from '@/api/ssafy'
import { procurementApi } from '@/api/procurement'

function todayStr() {
  return new Date().toISOString().slice(0, 10)
}

export const useWorkflowStore = defineStore('workflow', () => {
  const recommendation = ref([])
  const taskList = ref([])
  const selectedDate = ref(todayStr())
  const loading = ref(false)
  const error = ref(null)
  const lastFetched = ref(null)

  async function fetchRecommendation(date, force) {
    if (date) selectedDate.value = date
    loading.value = true
    error.value = null
    try {
      const res = await worksApi.aiRecommend(selectedDate.value, force)
      error.value = res.data.error
      recommendation.value = res.data.items || []
      taskList.value = res.data.items || []
      lastFetched.value = new Date()
    } catch (e) {
      error.value = 'AI unavailable'
      recommendation.value = []
      taskList.value = []
    } finally {
      loading.value = false
    }
  }

  async function pollStatuses() {
    try {
      const res = await worksApi.statusSummary(selectedDate.value)
      const statusMap = new Map((res.data.items || []).map((it) => [it.id, it]))
      recommendation.value = recommendation.value.map((item) => {
        const live = statusMap.get(item.id)
        if (!live) return item
        return { ...item, status: live.status, done: live.done }
      })
    } catch {
      // 폴링 실패는 조용히 무시 — 다음 주기에 다시 시도
    }
  }

  async function updateTaskStatus(item, done) {
    const [sourceType, sourceId] = item.id.split(':')
    if (sourceType === 'task') {
      await worksApi.updateTask(sourceId, {
        status: done ? 'DONE' : 'TODO',
        completed_at: done ? new Date().toISOString() : null,
      })
    } else if (sourceType === 'order') {
      await ssafyApi.updateOrder(sourceId, { shippeddate: done ? todayStr() : null })
    } else if (sourceType === 'purchase_order') {
      const res = await procurementApi.purchaseOrders()
      const po = res.data.find((p) => String(p.id) === String(sourceId))
      if (po) {
        await procurementApi.updatePurchaseOrder(sourceId, {
          ...po,
          status: done ? 'received' : 'ordered',
          receiveddate: done ? todayStr() : null,
        })
      }
    }
    recommendation.value = recommendation.value.map((it) =>
      it.id === item.id ? { ...it, done, status: done ? '완료' : it.status } : it,
    )
  }

  return {
    recommendation, taskList, selectedDate, loading, error, lastFetched,
    fetchRecommendation, pollStatuses, updateTaskStatus,
  }
})
