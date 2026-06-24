import http from './http'

export const analyticsApi = {
  demandInsight: (summary) => http.post('analytics/demand-insight/', { summary }),
}
