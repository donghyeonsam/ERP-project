import http from './http'

export const payrollApi = {
  salaries: () => http.get('payroll/salaries/'),
  createSalary: (data) => http.post('payroll/salaries/', data),
  updateSalary: (id, data) => http.put(`payroll/salaries/${id}/`, data),
  deleteSalary: (id) => http.delete(`payroll/salaries/${id}/`),

  bonuses: () => http.get('payroll/bonuses/'),
  createBonus: (data) => http.post('payroll/bonuses/', data),
  updateBonus: (id, data) => http.put(`payroll/bonuses/${id}/`, data),
  deleteBonus: (id) => http.delete(`payroll/bonuses/${id}/`),

  yearEndSettlements: () => http.get('payroll/year-end-settlements/'),
  createYearEnd: (data) => http.post('payroll/year-end-settlements/', data),
  updateYearEnd: (id, data) => http.put(`payroll/year-end-settlements/${id}/`, data),

  severances: () => http.get('payroll/severances/'),
  createSeverance: (data) => http.post('payroll/severances/', data),
  updateSeverance: (id, data) => http.put(`payroll/severances/${id}/`, data),
}
