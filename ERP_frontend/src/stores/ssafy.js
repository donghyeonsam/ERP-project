import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ssafyApi } from '@/api/ssafy'

export const useSsafyStore = defineStore('ssafy', () => {
  const orders = ref([])
  const orderDetails = ref([])
  const customers = ref([])
  const products = ref([])
  const categories = ref([])
  const loading = ref(false)

  async function fetchOrders(params) {
    loading.value = true
    try {
      const res = await ssafyApi.orders(params)
      orders.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchOrderDetails(params) {
    const res = await ssafyApi.orderDetails(params)
    orderDetails.value = res.data
  }

  async function fetchCustomers(params) {
    const res = await ssafyApi.customers(params)
    customers.value = res.data
  }

  async function fetchProducts(params) {
    const res = await ssafyApi.products(params)
    products.value = res.data
  }

  async function fetchCategories() {
    const res = await ssafyApi.categories()
    categories.value = res.data
  }

  return { orders, orderDetails, customers, products, categories, loading, fetchOrders, fetchOrderDetails, fetchCustomers, fetchProducts, fetchCategories }
})
