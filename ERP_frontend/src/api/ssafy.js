import http from './http'

export const ssafyApi = {
  categories: () => http.get('ssafy/categories/'),
  suppliers: () => http.get('ssafy/suppliers/'),
  customers: (params) => http.get('ssafy/customers/', { params }),
  customer: (id) => http.get(`ssafy/customers/${id}/`),
  products: (params) => http.get('ssafy/products/', { params }),
  orders: (params) => http.get('ssafy/orders/', { params }),
  orderDetails: (params) => http.get('ssafy/order-details/', { params }),
  shippers: () => http.get('ssafy/shippers/'),
  regions: () => http.get('ssafy/regions/'),
  territories: (params) => http.get('ssafy/territories/', { params }),
}
