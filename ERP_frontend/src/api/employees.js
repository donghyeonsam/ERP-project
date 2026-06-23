import http from './http'

export const employeesApi = {
  list: () => http.get('employees/'),
  me: () => http.get('employees/me/'),
  get: (id) => http.get(`employees/${id}/`),
  orgChart: () => http.get('employees/org-chart/'),
  territories: () => http.get('employees/territories/'),
}
