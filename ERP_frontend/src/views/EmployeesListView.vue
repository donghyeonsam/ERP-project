<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-people me-2"></i>임직원</h5>
    </div>

    <div class="card erp-card mb-3">
      <div class="card-body py-2">
        <input v-model="search" type="text" class="form-control form-control-sm" placeholder="이름, 직급, 도시 검색..." style="max-width:280px" />
      </div>
    </div>

    <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else class="row g-3">
      <div v-for="emp in filtered" :key="emp.employeeid" class="col-md-4 col-lg-3">
        <div class="card erp-card emp-card h-100" @click="router.push(`/employees/${emp.employeeid}`)">
          <div class="card-body text-center">
            <div class="emp-avatar mx-auto mb-2">{{ initial(emp) }}</div>
            <div class="fw-semibold">{{ emp.lastname }}{{ emp.firstname }}</div>
            <div class="text-muted small">{{ emp.title }}</div>
            <div class="text-muted mt-1" style="font-size:0.72rem">{{ emp.city }}, {{ emp.country }}</div>
          </div>
        </div>
      </div>
      <div v-if="filtered.length === 0" class="col-12 text-center text-muted py-5">직원이 없습니다</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEmployeeStore } from '@/stores/employees'

const router = useRouter()
const store = useEmployeeStore()
const search = ref('')

const filtered = computed(() => {
  if (!search.value) return store.employees
  const q = search.value.toLowerCase()
  return store.employees.filter(e =>
    `${e.lastname}${e.firstname}`.toLowerCase().includes(q) ||
    (e.title||'').toLowerCase().includes(q) ||
    (e.city||'').toLowerCase().includes(q),
  )
})

function initial(emp) { return (emp.lastname || '').charAt(0) || 'E' }

onMounted(() => store.fetchAll())
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.emp-card { cursor: pointer; transition: box-shadow 0.15s; }
.emp-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
.emp-avatar {
  width: 52px; height: 52px; background: #2563eb; color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.3rem;
}
</style>
