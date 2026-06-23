import http from './http'

export const procurementApi = {
  productCosts: () => http.get('procurement/product-costs/'),
  purchaseOrders: () => http.get('procurement/purchase-orders/'),
  createPurchaseOrder: (data) => http.post('procurement/purchase-orders/', data),
  updatePurchaseOrder: (id, data) => http.put(`procurement/purchase-orders/${id}/`, data),
  deletePurchaseOrder: (id) => http.delete(`procurement/purchase-orders/${id}/`),
  purchaseOrderDetails: (params) => http.get('procurement/purchase-order-details/', { params }),
  createPurchaseOrderDetail: (data) => http.post('procurement/purchase-order-details/', data),
  goodsReceipts: () => http.get('procurement/goods-receipts/'),
  createGoodsReceipt: (data) => http.post('procurement/goods-receipts/', data),
  updateGoodsReceipt: (id, data) => http.put(`procurement/goods-receipts/${id}/`, data),
  deleteGoodsReceipt: (id) => http.delete(`procurement/goods-receipts/${id}/`),
  materials: () => http.get('procurement/materials/'),
  boms: () => http.get('procurement/boms/'),
  bomComponents: (params) => http.get('procurement/bom-components/', { params }),
}
