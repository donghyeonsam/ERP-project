<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-cash-coin me-2"></i>급여관리</h5>
        <p class="text-muted small mb-0">{{ subtitle }}</p>
      </div>
    </div>

    <!-- 메인 토글 -->
    <div class="d-flex gap-2 mb-4">
      <button class="btn btn-sm" :class="activeMain === 'calc' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'calc'">급여 계산</button>
      <button class="btn btn-sm" :class="activeMain === 'bonus' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'bonus'">상여 관리</button>
      <button class="btn btn-sm" :class="activeMain === 'yearend' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'yearend'">연말 정산</button>
      <button class="btn btn-sm" :class="activeMain === 'severance' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'severance'">퇴직금 관리</button>
    </div>

    <!-- ===================== 급여 계산 ===================== -->
    <div v-if="activeMain === 'calc'">
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">대상 인원</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ calcKpi.count }}<span class="small fw-normal text-muted ms-1">명</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">총 지급액</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ fmtMoney(calcKpi.totalPayment) }}</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">총 공제액</div>
            <div class="fw-bold text-danger" style="font-size:1.4rem">{{ fmtMoney(calcKpi.totalDeduction) }}</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">실수령 합계</div>
            <div class="fw-bold text-success" style="font-size:1.4rem">{{ fmtMoney(calcKpi.totalNet) }}</div>
          </div>
        </div>
      </div>

      <div class="card erp-card mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">월</label>
              <select v-model="calcFilter.period" class="form-select form-select-sm">
                <option v-for="p in periodOptions" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">부서</label>
              <select v-model="calcFilter.department" class="form-select form-select-sm">
                <option value="">전체</option>
                <option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">상태</label>
              <select v-model="calcFilter.status" class="form-select form-select-sm">
                <option value="">전체</option>
                <option value="확정">확정</option>
                <option value="계산중">계산중</option>
              </select>
            </div>
            <div class="col-md-3 d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="calcFilter.department=''; calcFilter.status=''">
                <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>사번</th><th>성명</th><th>부서</th><th class="text-end">기본급</th>
                  <th class="text-end">직책수당</th><th class="text-end">초과수당</th>
                  <th class="text-end">총지급액</th><th class="text-end">총공제액</th>
                  <th class="text-end">실수령액</th><th>상태</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in filteredSalaries" :key="r.id">
                  <td class="small text-muted">{{ r.employee }}</td>
                  <td class="small fw-semibold">{{ r.employee_name }}</td>
                  <td class="small text-muted">{{ r.department || '-' }}</td>
                  <td class="small text-end">{{ fmtMoney(r.base_salary) }}</td>
                  <td class="small text-end">{{ fmtMoney(r.position_allowance) }}</td>
                  <td class="small text-end">{{ fmtMoney(r.overtime_pay) }}</td>
                  <td class="small text-end fw-semibold">{{ fmtMoney(r.total_payment) }}</td>
                  <td class="small text-end text-danger">{{ fmtMoney(r.total_deduction) }}</td>
                  <td class="small text-end fw-semibold text-success">{{ fmtMoney(r.net_pay) }}</td>
                  <td><span class="badge" :class="r.status === '확정' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'">{{ r.status }}</span></td>
                </tr>
                <tr v-if="filteredSalaries.length === 0">
                  <td colspan="10" class="text-center text-muted small py-4">조건에 맞는 급여 내역이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== 상여 관리 ===================== -->
    <div v-else-if="activeMain === 'bonus'" class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr><th>사번</th><th>성명</th><th>부서</th><th>상여종류</th><th>지급일</th><th class="text-end">금액</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="b in payrollStore.bonuses" :key="b.id">
                <td class="small text-muted">{{ b.employee }}</td>
                <td class="small fw-semibold">{{ b.employee_name }}</td>
                <td class="small text-muted">{{ b.department || '-' }}</td>
                <td class="small">{{ b.bonus_type }}</td>
                <td class="small text-muted">{{ b.pay_date }}</td>
                <td class="small text-end fw-semibold">{{ fmtMoney(b.amount) }}</td>
                <td><span class="badge bg-success-subtle text-success border border-success-subtle">{{ b.status }}</span></td>
              </tr>
              <tr v-if="payrollStore.bonuses.length === 0">
                <td colspan="7" class="text-center text-muted small py-4">상여 내역이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===================== 연말 정산 ===================== -->
    <div v-else-if="activeMain === 'yearend'" class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr><th>사번</th><th>성명</th><th>부서</th><th>연도</th><th class="text-end">총소득</th><th class="text-end">기납부세액</th><th class="text-end">결정세액</th><th class="text-end">환급/추가납부</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="y in payrollStore.yearEndSettlements" :key="y.id">
                <td class="small text-muted">{{ y.employee }}</td>
                <td class="small fw-semibold">{{ y.employee_name }}</td>
                <td class="small text-muted">{{ y.department || '-' }}</td>
                <td class="small">{{ y.year }}</td>
                <td class="small text-end">{{ fmtMoney(y.total_income) }}</td>
                <td class="small text-end">{{ fmtMoney(y.tax_withheld) }}</td>
                <td class="small text-end">{{ fmtMoney(y.determined_tax) }}</td>
                <td class="small text-end fw-semibold" :class="refundClass(y.refund_amount)">{{ fmtRefund(y.refund_amount) }}</td>
                <td><span class="badge bg-success-subtle text-success border border-success-subtle">{{ y.status }}</span></td>
              </tr>
              <tr v-if="payrollStore.yearEndSettlements.length === 0">
                <td colspan="9" class="text-center text-muted small py-4">연말정산 내역이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===================== 퇴직금 관리 ===================== -->
    <div v-else class="card erp-card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr><th>사번</th><th>성명</th><th>부서</th><th class="text-end">근속연수</th><th class="text-end">평균월급</th><th class="text-end">예상 퇴직금</th><th>상태</th></tr>
            </thead>
            <tbody>
              <tr v-for="s in payrollStore.severances" :key="s.id">
                <td class="small text-muted">{{ s.employee }}</td>
                <td class="small fw-semibold">{{ s.employee_name }}</td>
                <td class="small text-muted">{{ s.department || '-' }}</td>
                <td class="small text-end">{{ s.years_of_service }}년</td>
                <td class="small text-end">{{ fmtMoney(s.avg_monthly_wage) }}</td>
                <td class="small text-end fw-semibold">{{ fmtMoney(s.calculated_amount) }}</td>
                <td><span class="badge bg-info-subtle text-info border border-info-subtle">{{ s.status }}</span></td>
              </tr>
              <tr v-if="payrollStore.severances.length === 0">
                <td colspan="7" class="text-center text-muted small py-4">퇴직금 내역이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { usePayrollStore } from '@/stores/payroll'

const payrollStore = usePayrollStore()

const activeMain = ref('calc')
const subtitle = computed(() => ({
  calc: '월별 급여를 계산하고 지급 명세를 관리합니다',
  bonus: '설날·추석·성과 등 상여 지급 내역을 관리합니다',
  yearend: '연말정산 결과와 환급/추가납부 내역을 관리합니다',
  severance: '근속연수 기준 예상 퇴직금을 관리합니다',
}[activeMain.value]))

function fmtMoney(v) {
  if (v == null) return '-'
  if (typeof v === 'string') return v // '비공개' 등 마스킹된 문자열
  return Math.round(Number(v)).toLocaleString('ko-KR') + '원'
}
function fmtRefund(v) {
  if (typeof v === 'string') return v
  const n = Number(v)
  return (n >= 0 ? '+' : '') + Math.round(n).toLocaleString('ko-KR') + '원'
}
function refundClass(v) {
  if (typeof v === 'string') return 'text-muted'
  return Number(v) >= 0 ? 'text-success' : 'text-danger'
}

// ===================== 급여 계산 =====================
const periodOptions = computed(() => [...new Set(payrollStore.salaries.map((s) => s.period))].sort().reverse())
const departmentOptions = computed(() => [...new Set(payrollStore.salaries.map((s) => s.department).filter(Boolean))].sort())

const calcFilter = reactive({ period: '', department: '', status: '' })

const filteredSalaries = computed(() => {
  let list = payrollStore.salaries
  if (calcFilter.period) list = list.filter((s) => s.period === calcFilter.period)
  if (calcFilter.department) list = list.filter((s) => s.department === calcFilter.department)
  if (calcFilter.status) list = list.filter((s) => s.status === calcFilter.status)
  return list
})

const calcKpi = computed(() => {
  const list = filteredSalaries.value
  const numeric = (v) => (typeof v === 'string' ? 0 : Number(v))
  return {
    count: new Set(list.map((s) => s.employee)).size,
    totalPayment: list.reduce((s, r) => s + numeric(r.total_payment), 0),
    totalDeduction: list.reduce((s, r) => s + numeric(r.total_deduction), 0),
    totalNet: list.reduce((s, r) => s + numeric(r.net_pay), 0),
  }
})

onMounted(async () => {
  await payrollStore.fetchAll()
  if (periodOptions.value.length) calcFilter.period = periodOptions.value[0]
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
</style>
