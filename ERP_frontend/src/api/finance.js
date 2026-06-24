import http from './http'

export const financeApi = {
  budgets: () => http.get('finance/budgets/'),
  expenses: () => http.get('finance/expenses/'),
  accountsReceivable: () => http.get('finance/accounts-receivable/'),
  accountsPayable: () => http.get('finance/accounts-payable/'),
  updateAccountsReceivable: (id, data) => http.put(`finance/accounts-receivable/${id}/`, data),
  updateAccountsPayable: (id, data) => http.put(`finance/accounts-payable/${id}/`, data),
}
