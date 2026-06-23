<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-building me-2"></i>고객사</h5>
    </div>

    <div class="card erp-card mb-3">
      <div class="card-body py-2 d-flex gap-2">
        <input v-model="search" type="text" class="form-control form-control-sm" placeholder="회사명, 국가 검색..." style="max-width:250px" />
        <input v-model="countryFilter" type="text" class="form-control form-control-sm" placeholder="국가 필터..." style="max-width:150px" />
      </div>
    </div>

    <div v-if="ssafyStore.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr><th>고객ID</th><th>회사명</th><th>담당자</th><th>도시</th><th>국가</th><th>전화</th></tr>
            </thead>
            <tbody>
              <tr v-for="c in filtered" :key="c.customerid" class="cursor-pointer" @click="router.push(`/customers/${c.customerid}`)">
                <td class="small text-muted">{{ c.customerid }}</td>
                <td class="small fw-semibold">{{ c.companyname }}</td>
                <td class="small">{{ c.contactname }}</td>
                <td class="small text-muted">{{ c.city }}</td>
                <td class="small text-muted">{{ c.country }}</td>
                <td class="small text-muted">{{ c.phone }}</td>
              </tr>
              <tr v-if="filtered.length === 0">
                <td colspan="6" class="text-center text-muted small py-4">데이터 없음</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSsafyStore } from '@/stores/ssafy'

const router = useRouter()
const ssafyStore = useSsafyStore()
const search = ref('')
const countryFilter = ref('')

const filtered = computed(() => {
  let list = ssafyStore.customers
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c => (c.companyname||'').toLowerCase().includes(q) || (c.country||'').toLowerCase().includes(q))
  }
  if (countryFilter.value) list = list.filter(c => (c.country||'').toLowerCase().includes(countryFilter.value.toLowerCase()))
  return list
})

onMounted(() => ssafyStore.fetchCustomers())
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.cursor-pointer { cursor: pointer; }
</style>
