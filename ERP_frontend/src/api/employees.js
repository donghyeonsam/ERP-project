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
}
