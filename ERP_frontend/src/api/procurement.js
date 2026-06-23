import http from './http'

export const procurementApi = {
  productCosts: () => http.get('procurement/product-costs/'),
  purchaseOrders: () => http.get('procurement/purchase-orders/'),
  purchaseOrderDetails: (params) => http.get('procurement/purchase-order-details/', { params }),
  goodsReceipts: () => http.get('procurement/goods-receipts/'),
  materials: () => http.get('procurement/materials/'),
  boms: () => http.get('procurement/boms/'),
  bomComponents: (params) => http.get('procurement/bom-components/', { params }),
}
