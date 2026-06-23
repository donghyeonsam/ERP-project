import http from './http'

export const financeApi = {
  expenses: () => http.get('finance/expenses/'),
  accountsReceivable: () => http.get('finance/accounts-receivable/'),
  accountsPayable: () => http.get('finance/accounts-payable/'),
}
