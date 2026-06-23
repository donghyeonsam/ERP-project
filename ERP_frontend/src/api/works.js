import http from './http'

export const worksApi = {
  calendarEvents: () => http.get('works/calendar-events/'),
  tasks: () => http.get('works/tasks/'),
  taskComments: (taskId) => http.get(`works/task-comments/?task=${taskId}`),
  createTask: (data) => http.post('works/tasks/', data),
  updateTask: (id, data) => http.patch(`works/tasks/${id}/`, data),
  deleteTask: (id) => http.delete(`works/tasks/${id}/`),
  notifications: () => http.get('works/notifications/'),
  memos: () => http.get('works/memos/'),
  createMemo: (content) => http.post('works/memos/', { content }),
  updateMemo: (id, content) => http.put(`works/memos/${id}/`, { content }),
  deleteMemo: (id) => http.delete(`works/memos/${id}/`),
}
