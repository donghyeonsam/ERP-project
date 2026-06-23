import { defineStore } from 'pinia'
import { ref } from 'vue'
import { worksApi } from '@/api/works'

export const useWorksStore = defineStore('works', () => {
  const tasks = ref([])
  const calendarEvents = ref([])
  const notifications = ref([])
  const loading = ref(false)

  async function fetchTasks() {
    loading.value = true
    try {
      const res = await worksApi.tasks()
      tasks.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchCalendarEvents() {
    const res = await worksApi.calendarEvents()
    calendarEvents.value = res.data
  }

  async function fetchNotifications() {
    const res = await worksApi.notifications()
    notifications.value = res.data
  }

  async function createTask(data) {
    const res = await worksApi.createTask(data)
    tasks.value.push(res.data)
    return res.data
  }

  return { tasks, calendarEvents, notifications, loading, fetchTasks, fetchCalendarEvents, fetchNotifications, createTask }
})
