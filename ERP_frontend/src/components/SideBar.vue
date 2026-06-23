<template>
  <aside class="erp-sidebar d-flex flex-column">
    <nav class="flex-grow-1 py-2">
      <RouterLink
        v-for="item in topItems"
        :key="item.name"
        :to="item.to"
        class="sidebar-item"
        :class="{ active: isActive(item.to) }"
      >
        <i :class="['bi', item.icon, 'sidebar-icon']"></i>
        <span class="sidebar-label">{{ item.label }}</span>
      </RouterLink>

      <!-- Dashboard expandable -->
      <div>
        <button
          class="sidebar-item sidebar-toggle w-100 text-start"
          :class="{ active: isDashboardActive }"
          @click="dashboardOpen = !dashboardOpen"
        >
          <i class="bi bi-grid sidebar-icon"></i>
          <span class="sidebar-label">대시보드</span>
          <i :class="['bi ms-auto', dashboardOpen ? 'bi-chevron-up' : 'bi-chevron-down']" style="font-size:0.7rem"></i>
        </button>
        <div v-if="dashboardOpen" class="sidebar-submenu">
          <RouterLink
            v-for="sub in dashboardItems"
            :key="sub.name"
            :to="sub.to"
            class="sidebar-subitem"
            :class="{ active: isActive(sub.to) }"
          >
            <i :class="['bi', sub.icon, 'me-2']" style="font-size:0.75rem"></i>
            {{ sub.label }}
          </RouterLink>
        </div>
      </div>
    </nav>

    <!-- 레벨 표시 -->
    <div class="sidebar-footer">
      <div class="level-badge">
        <i class="bi bi-shield-check me-1"></i>Lv.{{ userLevel }}
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const dashboardOpen = ref(false)

const userLevel = computed(() => authStore.user?.level || 0)

const topItems = [
  { label: '홈', icon: 'bi-house', to: '/' },
  { label: '전자결재', icon: 'bi-file-earmark-check', to: '/eapproval' },
  { label: 'Works', icon: 'bi-kanban', to: '/works' },
  { label: '캘린더', icon: 'bi-calendar3', to: '/calendar' },
  { label: '메모', icon: 'bi-journal-text', to: '/memo' },
  { label: '근태', icon: 'bi-clock-history', to: '/attendance' },
  { label: '임직원', icon: 'bi-people', to: '/employees' },
  { label: '고객사', icon: 'bi-building', to: '/customers' },
]

const dashboardItems = computed(() => {
  const lv = userLevel.value
  const items = []
  if (lv >= 5) items.push({ label: '경영', icon: 'bi-bar-chart-line', to: '/dashboard/management' })
  if (lv >= 5) items.push({ label: '영업', icon: 'bi-graph-up-arrow', to: '/dashboard/sales' })
  items.push({ label: '구매', icon: 'bi-cart3', to: '/dashboard/procurement' })
  items.push({ label: '생산·물류', icon: 'bi-gear', to: '/dashboard/production' })
  items.push({ label: '재무/회계', icon: 'bi-currency-exchange', to: '/dashboard/finance' })
  if (lv >= 4) items.push({ label: '인사', icon: 'bi-person-badge', to: '/dashboard/hr' })
  return items
})

const isDashboardActive = computed(() =>
  ['/dashboard/management', '/dashboard/sales', '/dashboard/procurement',
   '/dashboard/production', '/dashboard/finance', '/dashboard/hr'].some((p) =>
    route.path.startsWith(p),
  ),
)

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<style scoped>
.erp-sidebar {
  position: fixed;
  top: var(--navbar-height);
  left: 0;
  width: var(--sidebar-width);
  height: calc(100vh - var(--navbar-height));
  background: var(--sidebar-bg);
  overflow-y: auto;
  z-index: 1030;
  border-right: 1px solid rgba(255,255,255,0.06);
}

.sidebar-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 6px;
  margin: 2px 8px;
  transition: background 0.15s, color 0.15s;
  border: none;
  background: none;
  cursor: pointer;
}
.sidebar-item:hover { background: rgba(255,255,255,0.07); color: #e2e8f0; }
.sidebar-item.active { background: var(--sidebar-active); color: #ffffff; }
.sidebar-toggle.active { background: rgba(37,99,235,0.2); color: #93c5fd; }

.sidebar-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
  margin-right: 10px;
  flex-shrink: 0;
}
.sidebar-label { flex: 1; }

.sidebar-submenu { margin-left: 8px; }

.sidebar-subitem {
  display: flex;
  align-items: center;
  padding: 7px 16px 7px 36px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.8rem;
  border-radius: 6px;
  margin: 1px 8px;
  transition: background 0.15s, color 0.15s;
}
.sidebar-subitem:hover { background: rgba(255,255,255,0.07); color: #cbd5e1; }
.sidebar-subitem.active { background: var(--sidebar-active); color: #ffffff; }

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.level-badge {
  font-size: 0.72rem;
  color: #64748b;
  display: flex;
  align-items: center;
}
</style>
