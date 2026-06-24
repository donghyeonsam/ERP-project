import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Auth (no shell) ──────────────────────────────────────────────
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { public: true },
    },

    // ── 홈 ──────────────────────────────────────────────────────────
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },

    // ── Works ────────────────────────────────────────────────────────
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
    },
    {
      path: '/workflow',
      name: 'workFlow',
      component: () => import('@/views/WorkFlowView.vue'),
    },
    {
      path: '/works',
      name: 'workList',
      component: () => import('@/views/WorkListView.vue'),
    },
    {
      path: '/works/create',
      name: 'workCreate',
      component: () => import('@/views/WorkCreateView.vue'),
    },
    {
      path: '/works/:id',
      name: 'workDetail',
      component: () => import('@/views/WorkDetailView.vue'),
    },

    // ── 경영 ─────────────────────────────────────────────────────────
    {
      path: '/dashboard/management',
      name: 'managementDashboard',
      component: () => import('@/views/ManagementDashBoardView.vue'),
    },
    {
      path: '/management/performance',
      name: 'managementPerformance',
      component: () => import('@/views/ManagementPerformanceView.vue'),
    },
    {
      path: '/management/reports',
      name: 'managementReports',
      component: () => import('@/views/ManagementReportView.vue'),
    },

    // ── 영업 ─────────────────────────────────────────────────────────
    {
      path: '/customers',
      name: 'customerList',
      component: () => import('@/views/CustomerListView.vue'),
    },
    {
      path: '/customers/:id',
      name: 'customerDetail',
      component: () => import('@/views/CustomerDetailView.vue'),
    },
    {
      path: '/dashboard/sales',
      name: 'salesDashboard',
      component: () => import('@/views/SalesDashboardView.vue'),
    },

    // ── 구매 ─────────────────────────────────────────────────────────
    {
      path: '/procurement/orders',
      name: 'procurementOrders',
      component: () => import('@/views/ProcurementOrdersView.vue'),
    },
    {
      path: '/dashboard/procurement',
      name: 'procurementBom',
      component: () => import('@/views/ProcurementBomView.vue'),
    },

    // ── 물류 ─────────────────────────────────────────────────────────
    {
      path: '/logistics/inbound',
      name: 'logisticsInbound',
      component: () => import('@/views/LogisticsInboundView.vue'),
    },
    {
      path: '/logistics/inventory',
      name: 'logisticsInventory',
      component: () => import('@/views/LogisticsInventoryView.vue'),
    },
    {
      path: '/logistics/delivery',
      name: 'logisticsDelivery',
      component: () => import('@/views/LogisticsDeliveryView.vue'),
    },

    // ── 재무 / 회계 ──────────────────────────────────────────────────
    {
      path: '/finance/cost',
      name: 'financeReceivable',
      component: () => import('@/views/FinanceReceivableView.vue'),
    },
    {
      path: '/finance/budget',
      name: 'financeBudget',
      component: () => import('@/views/FinanceBudgetView.vue'),
    },

    // ── 인사 ─────────────────────────────────────────────────────────
    {
      path: '/employees',
      name: 'employeeList',
      component: () => import('@/views/EmployeesListView.vue'),
    },
    {
      path: '/employees/:id',
      name: 'employeeDetail',
      component: () => import('@/views/EmployeeDetailView.vue'),
    },
    {
      path: '/hr/organization',
      name: 'hrOrganization',
      component: () => import('@/views/OrganizationView.vue'),
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: () => import('@/views/AttendanceView.vue'),
    },
    {
      path: '/attendance/vacation',
      name: 'vacation',
      component: () => import('@/views/VacationView.vue'),
    },
    {
      path: '/hr/salary',
      name: 'salary',
      component: () => import('@/views/SalaryView.vue'),
    },

    // ── Fallback ─────────────────────────────────────────────────────
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    const ok = await auth.restoreSession()
    if (!ok) return { name: 'login' }
  }
  return true
})

export default router
