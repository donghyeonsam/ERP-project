import http from './http'

export const logisticsApi = {
  vehicles: () => http.get('logistics/vehicles/'),
  dispatches: () => http.get('logistics/dispatches/'),
  createDispatch: (data) => http.post('logistics/dispatches/', data),
  updateDispatch: (id, data) => http.put(`logistics/dispatches/${id}/`, data),
  deleteDispatch: (id) => http.delete(`logistics/dispatches/${id}/`),
}
