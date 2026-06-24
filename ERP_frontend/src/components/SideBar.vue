<template>
  <aside class="erp-sidebar d-flex flex-column">
    <nav class="flex-grow-1 py-2">
      <!-- 홈 -->
      <RouterLink to="/" class="sidebar-item" :class="{ active: route.path === '/' }">
        <i class="bi bi-house sidebar-icon"></i>
        <span class="sidebar-label">홈</span>
      </RouterLink>

      <!-- 그룹 메뉴 -->
      <div v-for="group in menuGroups" :key="group.label">
        <button
          class="sidebar-item sidebar-toggle w-100 text-start"
          :class="{ active: isGroupActive(group) }"
          @click="toggle(group.label)"
        >
          <i :class="['bi', group.icon, 'sidebar-icon']"></i>
          <span class="sidebar-label">{{ group.label }}</span>
          <i :class="['bi ms-auto', openGroups[group.label] ? 'bi-chevron-up' : 'bi-chevron-down']" style="font-size:0.7rem"></i>
        </button>

        <div v-if="openGroups[group.label]" class="sidebar-submenu">
          <template v-for="item in group.items" :key="item.label">
            <!-- 3단계 서브그룹 (근태 관리 등) -->
            <template v-if="item.children">
              <button
                class="sidebar-subitem sidebar-toggle w-100 text-start"
                :class="{ active: isSubGroupActive(item) }"
                @click="toggleSub(item.label)"
              >
                <i :class="['bi', item.icon, 'me-2']" style="font-size:0.75rem"></i>
                <span class="flex-grow-1">{{ item.label }}</span>
                <i :class="['bi ms-auto', openSubs[item.label] ? 'bi-chevron-up' : 'bi-chevron-down']" style="font-size:0.65rem"></i>
              </button>
              <div v-if="openSubs[item.label]" class="sidebar-subsubmenu">
                <RouterLink
                  v-for="child in item.children"
                  :key="child.to"
                  :to="child.to"
                  class="sidebar-subsubitem"
                  :class="{ active: isActive(child.to, true) }"
                >
                  <i :class="['bi', child.icon, 'me-2']" style="font-size:0.7rem"></i>
                  {{ child.label }}
                </RouterLink>
              </div>
            </template>

            <!-- 2단계 일반 항목 -->
            <RouterLink
              v-else
              :to="item.to"
              class="sidebar-subitem"
              :class="{ active: isActive(item.to) }"
            >
              <i :class="['bi', item.icon, 'me-2']" style="font-size:0.75rem"></i>
              {{ item.label }}
            </RouterLink>
          </template>
        </div>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="level-badge">
        <i class="bi bi-shield-check me-1"></i>Lv.{{ userLevel }}
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const userLevel = computed(() => authStore.user?.level || 0)

const menuGroups = [
  {
    label: 'Works',
    icon: 'bi-kanban',
    items: [
      { label: '캘린더', icon: 'bi-calendar3', to: '/calendar' },
      { label: '워크 플로우', icon: 'bi-diagram-3', to: '/workflow' },
      { label: 'Work 관리', icon: 'bi-list-check', to: '/works' },
    ],
  },
  {
    label: '경영',
    icon: 'bi-bar-chart-line',
    items: [
      { label: '경영 대시보드', icon: 'bi-speedometer2', to: '/dashboard/management' },
      { label: '성과 분석', icon: 'bi-graph-up', to: '/management/performance' },
      { label: '경영 보고서', icon: 'bi-file-earmark-bar-graph', to: '/management/reports' },
    ],
  },
  {
    label: '영업',
    icon: 'bi-graph-up-arrow',
    items: [
      { label: '거래처 관리', icon: 'bi-building', to: '/customers' },
      { label: '영업 대시보드', icon: 'bi-speedometer2', to: '/dashboard/sales' },
    ],
  },
  {
    label: '구매',
    icon: 'bi-cart3',
    items: [
      { label: '발주 관리', icon: 'bi-file-earmark-text', to: '/procurement/orders' },
      { label: 'BOM 관리', icon: 'bi-diagram-3', to: '/dashboard/procurement' },
    ],
  },
  {
    label: '물류',
    icon: 'bi-truck',
    items: [
      { label: '입고 관리', icon: 'bi-box-arrow-in-down', to: '/logistics/inbound' },
      { label: '재고 관리', icon: 'bi-boxes', to: '/logistics/inventory' },
      { label: '배송 관리', icon: 'bi-truck', to: '/logistics/delivery' },
    ],
  },
  {
    label: '재무 / 회계',
    icon: 'bi-currency-exchange',
    items: [
      { label: '채권채무관리', icon: 'bi-receipt-cutoff', to: '/finance/cost' },
      { label: '예산 관리', icon: 'bi-piggy-bank', to: '/finance/budget' },
    ],
  },
  {
    label: '인사',
    icon: 'bi-person-badge',
    items: [
      { label: '인사 마스터', icon: 'bi-people', to: '/employees' },
      { label: '조직 관리', icon: 'bi-diagram-2', to: '/hr/organization' },
      {
        label: '근태 관리',
        icon: 'bi-clock-history',
        children: [
          { label: '근태 관리', icon: 'bi-calendar-check', to: '/attendance' },
          { label: '휴가 관리', icon: 'bi-calendar-minus', to: '/attendance/vacation' },
        ],
      },
      { label: '급여 관리', icon: 'bi-cash-coin', to: '/hr/salary' },
    ],
  },
]

const openGroups = reactive({})
const openSubs = reactive({})

// 현재 경로와 일치하는 그룹·서브그룹은 자동 열기
function initOpen() {
  menuGroups.forEach((group) => {
    const groupActive = group.items.some((item) =>
      item.children
        ? item.children.some((c) => route.path.startsWith(c.to))
        : route.path.startsWith(item.to),
    )
    if (groupActive) {
      openGroups[group.label] = true
      group.items.forEach((item) => {
        if (item.children && item.children.some((c) => route.path.startsWith(c.to))) {
          openSubs[item.label] = true
        }
      })
    }
  })
}
initOpen()

function toggle(label) {
  openGroups[label] = !openGroups[label]
}
function toggleSub(label) {
  openSubs[label] = !openSubs[label]
}

function isActive(to, exact = false) {
  if (to === '/') return route.path === '/'
  if (exact) return route.path === to
  return route.path === to || route.path.startsWith(to + '/')
}

function isGroupActive(group) {
  return group.items.some((item) =>
    item.children
      ? item.children.some((c) => isActive(c.to))
      : isActive(item.to),
  )
}

function isSubGroupActive(item) {
  return item.children?.some((c) => isActive(c.to)) ?? false
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
  border: none;
  background: none;
  cursor: pointer;
  width: calc(100% - 16px);
}
.sidebar-subitem:hover { background: rgba(255,255,255,0.07); color: #cbd5e1; }
.sidebar-subitem.active { background: var(--sidebar-active); color: #ffffff; }

.sidebar-subsubmenu { margin-left: 8px; }

.sidebar-subsubitem {
  display: flex;
  align-items: center;
  padding: 6px 16px 6px 52px;
  color: #475569;
  text-decoration: none;
  font-size: 0.75rem;
  border-radius: 6px;
  margin: 1px 8px;
  transition: background 0.15s, color 0.15s;
}
.sidebar-subsubitem:hover { background: rgba(255,255,255,0.07); color: #cbd5e1; }
.sidebar-subsubitem.active { background: var(--sidebar-active); color: #ffffff; }

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
