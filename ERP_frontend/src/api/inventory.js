import http from './http'

export const inventoryApi = {
  countPlans: () => http.get('inventory/count-plans/'),
  createCountPlan: (data) => http.post('inventory/count-plans/', data),
  updateCountPlan: (id, data) => http.put(`inventory/count-plans/${id}/`, data),
  deleteCountPlan: (id) => http.delete(`inventory/count-plans/${id}/`),
  countItems: (params) => http.get('inventory/count-items/', { params }),
  createCountItem: (data) => http.post('inventory/count-items/', data),
  updateCountItem: (id, data) => http.put(`inventory/count-items/${id}/`, data),
}
