import http from './http'

export const employeesApi = {
  list: () => http.get('employees/'),
  me: () => http.get('employees/me/'),
  get: (id) => http.get(`employees/${id}/`),
  orgChart: () => http.get('employees/org-chart/'),
  territories: () => http.get('employees/territories/'),
}

export const attendanceApi = {
  today: () => http.get('employees/attendance/today/'),
  checkin: (time) => http.patch('employees/attendance/today/', { checkin_time: time }),
  checkout: (time) => http.patch('employees/attendance/today/', { checkout_time: time }),
  list: (month) => http.get(`employees/attendance/${month ? `?month=${month}` : ''}`),
  adminList: (params) => http.get('employees/attendance/admin/', { params }),
  manualCreate: (data) => http.post('employees/attendance/manual/', data),
}

export const leaveApi = {
  list: (params) => http.get('employees/leave-requests/', { params }),
  create: (data) => http.post('employees/leave-requests/', data),
  approve: (id) => http.post(`employees/leave-requests/${id}/approve/`),
  reject: (id) => http.post(`employees/leave-requests/${id}/reject/`),
  balances: () => http.get('employees/leave-balances/'),
}
