import http from './http'

export const worksApi = {
  calendarEvents: () => http.get('works/calendar-events/'),
  createCalendarEvent: (data) => http.post('works/calendar-events/', data),
  updateCalendarEvent: (id, data) => http.put(`works/calendar-events/${id}/`, data),
  deleteCalendarEvent: (id) => http.delete(`works/calendar-events/${id}/`),
  tasks: () => http.get('works/tasks/'),
  taskComments: (taskId) => http.get(`works/task-comments/?task=${taskId}`),
  createTask: (data) => http.post('works/tasks/', data),
  updateTask: (id, data) => http.patch(`works/tasks/${id}/`, data),
  deleteTask: (id) => http.delete(`works/tasks/${id}/`),
  notifications: () => http.get('works/notifications/'),
  memos: () => http.get('works/memos/'),
  createMemo: (content) => http.post('works/memos/', { content }),
  updateMemo: (id, content) => http.put(`works/memos/${id}/`, { content }),
  togglePinMemo: (id, isPinned) => http.put(`works/memos/${id}/`, { is_pinned: isPinned }),
  deleteMemo: (id) => http.delete(`works/memos/${id}/`),
}
