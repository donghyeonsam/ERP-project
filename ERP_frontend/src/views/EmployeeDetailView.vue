<template>
  <div style="max-width:720px">
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-sm btn-outline-secondary" @click="$router.back()"><i class="bi bi-arrow-left"></i></button>
      <h5 class="fw-bold mb-0">직원 프로필</h5>
    </div>

    <div v-if="store.loading" class="text-center py-5"><span class="spinner-border"></span></div>
    <div v-else-if="emp" class="row g-3">
      <div class="col-md-4">
        <div class="card erp-card text-center p-4">
          <div class="emp-avatar mx-auto mb-3">{{ initial(emp) }}</div>
          <h6 class="fw-bold mb-0">{{ emp.lastname }}{{ emp.firstname }}</h6>
          <div class="text-muted small mb-2">{{ emp.title }}</div>
          <div v-if="emp.reports_to_name" class="text-muted small">보고: {{ emp.reports_to_name }}</div>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card erp-card">
          <div class="card-body">
            <h6 class="fw-semibold mb-3 border-bottom pb-2">기본 정보</h6>
            <div class="row g-2">
              <div class="col-6" v-for="field in infoFields" :key="field.label">
                <div class="small text-muted">{{ field.label }}</div>
                <div class="small fw-semibold">{{ field.value || '-' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center text-muted py-5">직원 정보를 찾을 수 없습니다</div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEmployeeStore } from '@/stores/employees'

const route = useRoute()
const store = useEmployeeStore()
const emp = computed(() => store.current)

const infoFields = computed(() => [
  { label: '사원번호', value: emp.value?.employeeid },
  { label: '생년월일', value: fmtDate(emp.value?.birthdate) },
  { label: '입사일', value: fmtDate(emp.value?.hiredate) },
  { label: '직통번호', value: emp.value?.homephone },
  { label: '도시', value: emp.value?.city },
  { label: '국가', value: emp.value?.country },
  { label: '주소', value: emp.value?.address },
  { label: '우편번호', value: emp.value?.postalcode },
])

function initial(e) { return (e?.lastname || '').charAt(0) || 'E' }
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '-' }

onMounted(() => store.fetchOne(route.params.id))
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.emp-avatar {
  width: 72px; height: 72px; background: #2563eb; color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.8rem;
}
</style>
