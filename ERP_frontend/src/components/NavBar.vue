<template>
  <nav class="navbar navbar-expand navbar-light fixed-top erp-navbar px-3">
    <!-- Logo + Brand -->
    <RouterLink class="navbar-brand d-flex align-items-center gap-2" to="/">
      <div class="brand-logo">S</div>
      <span class="brand-name">SSAFY_International</span>
    </RouterLink>

    <div class="d-flex align-items-center ms-auto gap-3">
      <!-- Search -->
      <div class="search-wrapper position-relative">
        <div class="input-group input-group-sm search-box">
          <span class="input-group-text bg-light border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input
            v-model="searchQuery"
            type="text"
            class="form-control bg-light border-start-0"
            placeholder="메뉴 또는 직원 검색..."
            @keyup.enter="handleSearch"
            @input="onSearchInput"
            @blur="hideDropdown"
            @focus="onSearchInput"
          />
        </div>
        <!-- 검색 드롭다운 -->
        <div v-if="showSearchDrop && searchSuggestions.length" class="search-dropdown shadow-sm">
          <div
            v-for="s in searchSuggestions"
            :key="s.route"
            class="search-item"
            @mousedown.prevent="goTo(s.route)"
          >
            <i :class="['bi', s.icon, 'me-2 text-primary', 'flex-shrink-0']"></i>
            <div class="d-flex flex-column min-w-0">
              <span class="small fw-semibold">{{ s.label }}</span>
              <span v-if="s.group" class="search-group-hint">{{ s.group }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Notification bell -->
      <div class="position-relative">
        <button class="btn btn-link p-1 text-secondary" @click="showNotifications = !showNotifications">
          <i class="bi bi-bell fs-5"></i>
          <span v-if="unreadNotifications > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size:0.6rem">
            {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
          </span>
        </button>
        <div v-if="showNotifications" class="notification-dropdown shadow-sm">
          <div class="p-2 border-bottom fw-semibold small">알림</div>
          <div v-if="notifications.length === 0" class="p-3 text-muted small text-center">새 알림이 없습니다</div>
          <div
            v-for="n in notifications.slice(0, 5)"
            :key="n.id"
            class="notification-item p-2 border-bottom"
          >
            <div class="small fw-semibold">{{ n.title || '알림' }}</div>
            <div class="text-muted" style="font-size:0.75rem">{{ n.message || n.content }}</div>
          </div>
        </div>
      </div>

      <!-- Profile dropdown -->
      <div class="dropdown">
        <button
          class="btn btn-link d-flex align-items-center gap-2 text-dark text-decoration-none p-1"
          data-bs-toggle="dropdown"
        >
          <div class="avatar-circle">{{ userInitial }}</div>
          <span class="small fw-semibold d-none d-md-inline">{{ userName }}</span>
          <i class="bi bi-chevron-down small"></i>
        </button>
        <ul class="dropdown-menu dropdown-menu-end shadow-sm">
          <li>
            <RouterLink class="dropdown-item" :to="`/employees/${user?.employeeid}`">
              <i class="bi bi-person me-2"></i>내 프로필
            </RouterLink>
          </li>
          <li><hr class="dropdown-divider"></li>
          <li>
            <button class="dropdown-item text-danger" @click="handleLogout">
              <i class="bi bi-box-arrow-right me-2"></i>로그아웃
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  <div v-if="showNotifications" class="click-outside" @click="showNotifications = false"></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWorksStore } from '@/stores/works'

const router = useRouter()
const authStore = useAuthStore()
const worksStore = useWorksStore()

const searchQuery = ref('')
const showNotifications = ref(false)
const showSearchDrop = ref(false)

const FEATURES = [
  { label: '홈', icon: 'bi-house', route: '/', group: '', keywords: ['홈', 'home', '메인'] },
  // Works
  { label: '캘린더', icon: 'bi-calendar3', route: '/calendar', group: 'Works', keywords: ['캘린더', '일정', 'calendar'] },
  { label: '워크 플로우', icon: 'bi-diagram-3', route: '/workflow', group: 'Works', keywords: ['워크플로우', '칸반', 'workflow', 'kanban'] },
  { label: 'Work 관리', icon: 'bi-list-check', route: '/works', group: 'Works', keywords: ['works', '업무', '태스크', 'task', '워크'] },
  // 경영
  { label: '경영 대시보드', icon: 'bi-speedometer2', route: '/dashboard/management', group: '경영', keywords: ['경영', '대시보드', 'management'] },
  { label: '성과 분석', icon: 'bi-graph-up', route: '/management/performance', group: '경영', keywords: ['성과', '성과분석', 'performance'] },
  { label: '경영 보고서', icon: 'bi-file-earmark-bar-graph', route: '/management/reports', group: '경영', keywords: ['보고서', 'report', '경영보고'] },
  // 영업
  { label: '거래처 관리', icon: 'bi-building', route: '/customers', group: '영업', keywords: ['거래처', '고객', '영업', 'customer'] },
  { label: '영업 대시보드', icon: 'bi-speedometer2', route: '/dashboard/sales', group: '영업', keywords: ['영업', 'sales', '영업대시'] },
  // 구매
  { label: 'BOM 관리', icon: 'bi-diagram-3', route: '/dashboard/procurement', group: '구매', keywords: ['BOM', '레시피', '배합', 'bom'] },
  // 물류
  { label: '입고 관리', icon: 'bi-box-arrow-in-down', route: '/logistics/inbound', group: '물류', keywords: ['입고', '물류', 'inbound'] },
  { label: '재고 관리', icon: 'bi-boxes', route: '/logistics/inventory', group: '물류', keywords: ['물품', '재고', 'inventory', '실사', '유통기한'] },
  { label: '배송 관리', icon: 'bi-truck', route: '/logistics/delivery', group: '물류', keywords: ['배송', 'delivery', '물류'] },
  // 재무/회계
  { label: '채권채무관리', icon: 'bi-receipt-cutoff', route: '/finance/cost', group: '재무/회계', keywords: ['채권', '채무', '매출채권', '매입채무', '연체', 'receivable', 'payable', '재무'] },
  { label: '예산 관리', icon: 'bi-piggy-bank', route: '/finance/budget', group: '재무/회계', keywords: ['예산', 'budget', '재무'] },
  // 인사
  { label: '인사 마스터', icon: 'bi-people', route: '/employees', group: '인사', keywords: ['직원', '임직원', '인사', 'employee', '사원'] },
  { label: '조직 관리', icon: 'bi-diagram-2', route: '/hr/organization', group: '인사', keywords: ['조직', 'organization', '조직도'] },
  { label: '근태 관리', icon: 'bi-calendar-check', route: '/attendance', group: '인사 › 근태관리', keywords: ['근태', '출퇴근', 'attendance', '출근', '퇴근'] },
  { label: '휴가 관리', icon: 'bi-calendar-minus', route: '/attendance/vacation', group: '인사 › 근태관리', keywords: ['휴가', 'vacation', '연차'] },
  { label: '급여 관리', icon: 'bi-cash-coin', route: '/hr/salary', group: '인사', keywords: ['급여', '임금', 'salary', '월급'] },
]

const searchSuggestions = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return FEATURES.slice(0, 7)
  return FEATURES.filter((f) =>
    f.keywords.some((k) => k.includes(q)) || f.label.toLowerCase().includes(q) || (f.group && f.group.toLowerCase().includes(q))
  ).slice(0, 8)
})

const user = computed(() => authStore.user)
const userName = computed(() => {
  if (!user.value) return ''
  return `${user.value.lastname || ''}${user.value.firstname || ''}`
})
const userInitial = computed(() => userName.value.charAt(0) || 'U')
const notifications = computed(() => worksStore.notifications)
const unreadNotifications = computed(() => notifications.value.length)

onMounted(() => { worksStore.fetchNotifications().catch(() => {}) })

function onSearchInput() {
  showSearchDrop.value = true
}

function hideDropdown() {
  setTimeout(() => { showSearchDrop.value = false }, 150)
}

function goTo(route) {
  router.push(route)
  searchQuery.value = ''
  showSearchDrop.value = false
}

function handleSearch() {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return
  const match = FEATURES.find((f) => f.keywords.some((k) => k.includes(q)))
  if (match) {
    goTo(match.route)
  } else {
    router.push({ path: '/employees', query: { q: searchQuery.value } })
    searchQuery.value = ''
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.erp-navbar {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  height: var(--navbar-height);
  z-index: 1040;
}
.brand-logo {
  width: 32px;
  height: 32px;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
}
.brand-name {
  font-weight: 700;
  font-size: 1rem;
  color: #1e293b;
  white-space: nowrap;
}
.search-wrapper { position: relative; }
.search-box { width: 260px; }
.avatar-circle {
  width: 32px;
  height: 32px;
  background: #2563eb;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}
.search-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  z-index: 1060;
  overflow: hidden;
}
.search-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f8fafc;
  transition: background 0.1s;
}
.search-item:last-child { border-bottom: none; }
.search-item:hover { background: #f0f9ff; }
.search-group-hint {
  font-size: 0.65rem;
  color: #94a3b8;
  line-height: 1.2;
}

.notification-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 300px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  z-index: 1050;
  max-height: 360px;
  overflow-y: auto;
}
.notification-item:hover { background: #f8f9fa; }
.click-outside { position: fixed; inset: 0; z-index: 1045; }
</style>
