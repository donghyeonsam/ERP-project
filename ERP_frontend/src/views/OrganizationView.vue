<template>
  <div>
    <!-- 헤더 -->
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-diagram-3 me-2"></i>조직도</h5>
        <p class="text-muted small mb-0">부서별 조직 구조 및 보고 체계를 확인합니다</p>
      </div>
      <span class="badge bg-light text-dark border">총 {{ employees.length }}명</span>
    </div>

    <div v-if="loading" class="text-center py-5">
      <span class="spinner-border text-primary"></span>
    </div>

    <template v-else>
      <!-- ① CEO 섹션 -->
      <div class="d-flex flex-column align-items-center">
        <div class="ceo-card-wrap">
          <div class="ceo-card">
            <div class="ceo-avatar">{{ ceo?.name?.charAt(0) }}</div>
            <div class="ceo-body">
              <div class="ceo-name">{{ ceo?.name }}</div>
              <div class="ceo-subtitle">대표이사 · 경영지원부</div>
            </div>
            <span class="lv-badge lv-badge-5">LV 5</span>
          </div>
        </div>
        <div class="ceo-vline"></div>
      </div>

      <!-- 구분선 -->
      <div class="dept-section-label"><span>부서별 조직</span></div>

      <!-- ② 부서 카드 행 -->
      <div class="dept-grid">
        <div
          v-for="dept in deptList"
          :key="dept.name"
          class="dept-item"
          @click="toggleDept(dept.name)"
        >
          <div class="dept-card" :class="{ 'dept-card--active': activeDept === dept.name }">
            <div class="dept-icon" :class="`dept-icon--${deptKey(dept.name)}`">
              <i class="bi bi-people-fill"></i>
            </div>
            <div class="dept-info">
              <div class="dept-name">{{ dept.name }}</div>
              <div class="dept-sub">{{ dept.members.length }}명</div>
              <div v-if="dept.head" class="dept-head-label">
                <i class="bi bi-person-check me-1" style="font-size:0.65rem"></i>{{ dept.head.name }}
              </div>
            </div>
            <i
              class="bi dept-arrow"
              :class="activeDept === dept.name ? 'bi-chevron-up text-primary' : 'bi-chevron-down text-muted'"
            ></i>
          </div>
        </div>
      </div>

      <!-- ③ 부서원 확장 패널 — 프로필 카드 형식 -->
      <transition name="expand">
        <div v-if="activeDept && activeDeptData" class="panel-card erp-card mt-4">
          <!-- 패널 헤더 -->
          <div class="panel-header">
            <div class="panel-dot" :class="`panel-dot--${deptKey(activeDept)}`"></div>
            <span class="fw-semibold">{{ activeDept }}</span>
            <span class="badge bg-primary-subtle text-primary ms-2">{{ activeDeptData.members.length }}명</span>
            <button class="btn btn-sm btn-outline-secondary ms-auto" @click.stop="activeDept = null">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <!-- 부서원: 인사마스터와 동일한 프로필 카드 그리드 -->
          <div class="panel-body">
            <template v-for="(root, idx) in activeDeptData.tree" :key="root.employeeid">
              <hr v-if="idx > 0" class="my-4" />

              <!-- 리더 레이블 (보고 라인 구분) -->
              <div v-if="root.reports.length" class="group-label mb-3">
                <i class="bi bi-diagram-2 me-1"></i>
                <span class="fw-semibold">{{ root.name }}</span> 팀
                <span class="badge bg-secondary-subtle text-secondary ms-1">{{ root.reports.length + 1 }}명</span>
              </div>

              <!-- 카드 그리드: 리더 + 직속 부서원 모두 동일한 형태 -->
              <div class="emp-cards-grid">
                <!-- 리더 카드 (인사마스터와 동일, 상단 컬러 라인만 추가) -->
                <div
                  class="card erp-card emp-card"
                  :class="`emp-card--leader-${deptKey(activeDept)}`"
                  @click="goToEmployee(root.employeeid)"
                >
                  <div class="card-body text-center">
                    <div class="emp-avatar mx-auto mb-2" :class="`emp-avatar--lv${root.level || 1}`">
                      {{ root.name.charAt(0) }}
                    </div>
                    <div class="fw-semibold">{{ root.name }}</div>
                    <div class="text-muted small">{{ TITLE_KO[root.title] || root.title }}</div>
                    <div v-if="root.city" class="text-muted mt-1" style="font-size:0.72rem">
                      {{ root.city }}<span v-if="root.country">, {{ root.country }}</span>
                    </div>
                  </div>
                </div>

                <!-- 직속 부서원 카드들 — 인사마스터와 동일한 스타일 -->
                <div
                  v-for="rep in root.reports"
                  :key="rep.employeeid"
                  class="card erp-card emp-card"
                  @click="goToEmployee(rep.employeeid)"
                >
                  <div class="card-body text-center">
                    <div class="emp-avatar mx-auto mb-2" :class="`emp-avatar--lv${rep.level || 1}`">
                      {{ rep.name.charAt(0) }}
                    </div>
                    <div class="fw-semibold">{{ rep.name }}</div>
                    <div class="text-muted small">{{ TITLE_KO[rep.title] || rep.title }}</div>
                    <div v-if="rep.city" class="text-muted mt-1" style="font-size:0.72rem">
                      {{ rep.city }}<span v-if="rep.country">, {{ rep.country }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <div v-if="activeDeptData.tree.length === 0" class="text-muted small text-center py-4">
              멤버 정보가 없습니다.
            </div>
          </div>
        </div>
      </transition>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { employeesApi } from '@/api/employees'

const router = useRouter()
const loading = ref(true)
const employees = ref([])
const activeDept = ref(null)

const DEPT_ORDER = ['경영지원부', '영업팀', '물류팀', '인사팀']

const TITLE_LEVEL = {
  '대표이사': 5,
  'Vice President, Sales': 4,
  'Sales Manager': 3,
  'Inside Sales Coordinator': 2,
  'Sales Representative': 1,
}

const TITLE_KO = {
  '대표이사': '대표이사',
  'Vice President, Sales': '부사장',
  'Sales Manager': '팀장',
  'Inside Sales Coordinator': '주임',
  'Sales Representative': '사원',
}

const DEPT_KEYS = { '경영지원부': 'mgt', '영업팀': 'sales', '물류팀': 'logistics', '인사팀': 'hr' }
const deptKey = (name) => DEPT_KEYS[name] || 'mgt'

// ── 직원 가공 ──
const empMap = computed(() => {
  const m = {}
  employees.value.forEach((e) => {
    m[e.employeeid] = { ...e, name: `${e.lastname}${e.firstname}`, level: TITLE_LEVEL[e.title] || 0 }
  })
  return m
})

const ceo = computed(() => Object.values(empMap.value).find((e) => !e.reportsto) || null)

function buildTree(deptName) {
  const members = Object.values(empMap.value).filter((e) => e.department === deptName)
  const idSet = new Set(members.map((e) => e.employeeid))
  function node(emp) {
    return {
      ...emp,
      reports: members
        .filter((e) => e.reportsto === emp.employeeid)
        .sort((a, b) => (b.level || 0) - (a.level || 0))
        .map(node),
    }
  }
  return members
    .filter((e) => !idSet.has(e.reportsto))
    .sort((a, b) => (b.level || 0) - (a.level || 0))
    .map(node)
}

const deptList = computed(() =>
  DEPT_ORDER.map((name) => {
    const members = Object.values(empMap.value).filter((e) => e.department === name)
    if (!members.length) return null
    const tree = buildTree(name)
    const head = members.reduce((top, e) => ((e.level || 0) > (top?.level || -1) ? e : top), null)
    return { name, members, tree, head }
  }).filter(Boolean),
)

const activeDeptData = computed(() => deptList.value.find((d) => d.name === activeDept.value) || null)

function toggleDept(name) { activeDept.value = activeDept.value === name ? null : name }
function goToEmployee(id) { router.push(`/employees/${id}`) }

onMounted(async () => {
  try {
    const res = await employeesApi.list()
    employees.value = res.data
  } catch {
    // silent
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ── 공통 ── */
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }

/* ── CEO 카드 ── */
.ceo-card-wrap {
  background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
  border-radius: 16px; padding: 2px;
  box-shadow: 0 6px 24px rgba(30, 58, 95, 0.25);
}
.ceo-card {
  background: #fff; border-radius: 14px;
  padding: 18px 28px;
  display: flex; align-items: center; gap: 16px;
  min-width: 280px;
}
.ceo-avatar {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, #1e3a5f, #1d4ed8);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 800; flex-shrink: 0;
}
.ceo-body { flex: 1; }
.ceo-name { font-weight: 700; font-size: 1.05rem; color: #1e293b; }
.ceo-subtitle { font-size: 0.78rem; color: #64748b; margin-top: 3px; }
.ceo-vline { width: 2px; height: 20px; background: #cbd5e1; margin: 0 auto; }

/* ── 구분 레이블 ── */
.dept-section-label {
  text-align: center; font-size: 0.72rem; font-weight: 600;
  color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 16px; position: relative;
}
.dept-section-label::before,
.dept-section-label::after {
  content: ''; position: absolute; top: 50%; width: 35%; height: 1px; background: #e2e8f0;
}
.dept-section-label::before { right: 55%; }
.dept-section-label::after  { left:  55%; }

/* ── 부서 그리드 ── */
.dept-grid { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
.dept-item { display: flex; flex-direction: column; align-items: center; width: 188px; }

/* ── 부서 카드 ── */
.dept-card {
  width: 100%; background: #fff; border: 1.5px solid #e2e8f0;
  border-radius: 12px; padding: 14px; cursor: pointer;
  display: flex; align-items: flex-start; gap: 10px;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.1s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05); user-select: none;
}
.dept-card:hover { border-color: #93c5fd; box-shadow: 0 4px 14px rgba(59,130,246,0.12); transform: translateY(-1px); }
.dept-card--active { border-color: #3b82f6 !important; box-shadow: 0 4px 18px rgba(59,130,246,0.22) !important; background: #eff6ff; }

.dept-icon { width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.dept-icon--mgt       { background: #dbeafe; color: #1d4ed8; }
.dept-icon--sales     { background: #dcfce7; color: #15803d; }
.dept-icon--logistics { background: #fef9c3; color: #a16207; }
.dept-icon--hr        { background: #fce7f3; color: #be185d; }

.dept-info { flex: 1; min-width: 0; }
.dept-name { font-weight: 700; font-size: 0.9rem; color: #1e293b; }
.dept-sub  { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
.dept-head-label { font-size: 0.68rem; color: #94a3b8; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dept-arrow { font-size: 0.78rem; flex-shrink: 0; margin-top: 3px; }

/* ── 패널 ── */
.panel-card { overflow: hidden; }
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 20px; border-bottom: 1px solid #f1f5f9;
  background: #fff; border-radius: 12px 12px 0 0;
}
.panel-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.panel-dot--mgt       { background: #1d4ed8; }
.panel-dot--sales     { background: #15803d; }
.panel-dot--logistics { background: #a16207; }
.panel-dot--hr        { background: #be185d; }
.panel-body { padding: 24px; }

/* ── 트랜지션 ── */
.expand-enter-active { transition: all 0.22s ease; }
.expand-leave-active { transition: all 0.18s ease; }
.expand-enter-from { opacity: 0; transform: translateY(-10px); }
.expand-leave-to   { opacity: 0; transform: translateY(-10px); }

/* ── 그룹 레이블 ── */
.group-label { font-size: 0.78rem; color: #64748b; }

/* ── 직원 카드 그리드 (인사마스터와 동일) ── */
.emp-cards-grid { display: flex; flex-wrap: wrap; gap: 14px; }

/* ── 직원 프로필 카드 ── */
.emp-card {
  width: 120px; min-width: 110px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.1s;
}
.emp-card .card-body { padding: 16px 12px 14px; }
.emp-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.13) !important; transform: translateY(-2px); }

/* 리더 카드: 상단 컬러 라인으로 구분 */
.emp-card--leader-mgt       { border-top: 3px solid #1d4ed8; }
.emp-card--leader-sales     { border-top: 3px solid #15803d; }
.emp-card--leader-logistics { border-top: 3px solid #a16207; }
.emp-card--leader-hr        { border-top: 3px solid #be185d; }

/* ── 아바타 (인사마스터와 동일) ── */
.emp-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  background: #2563eb; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 700;
}
.emp-avatar--lv5 { background: #1e3a5f; }
.emp-avatar--lv4 { background: #1d4ed8; }
.emp-avatar--lv3 { background: #0369a1; }
.emp-avatar--lv2 { background: #0891b2; }
.emp-avatar--lv1 { background: #2563eb; }

/* ── LV 배지 (CEO 섹션용) ── */
.lv-badge {
  font-size: 0.63rem; font-weight: 700;
  padding: 2px 8px; border-radius: 999px; white-space: nowrap;
}
.lv-badge-5 { background: #1e3a5f; color: #fff; }
</style>
