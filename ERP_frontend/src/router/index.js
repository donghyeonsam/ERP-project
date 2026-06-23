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

    // ── App shell routes (guarded) ───────────────────────────────────
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
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
    {
      path: '/workflow',
      name: 'workFlow',
      component: () => import('@/views/WorkFlowView.vue'),
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: () => import('@/views/AttendanceView.vue'),
    },
    {
      path: '/memo',
      name: 'memo',
      component: () => import('@/views/MemoView.vue'),
    },
    {
      path: '/eapproval',
      name: 'eApproval',
      component: () => import('@/views/EApprovalView.vue'),
    },

    // ── Dashboards ───────────────────────────────────────────────────
    {
      path: '/dashboard/management',
      name: 'managementDashboard',
      component: () => import('@/views/ManagementDashBoardView.vue'),
    },
    {
      path: '/dashboard/sales',
      name: 'salesDashboard',
      component: () => import('@/views/SalesDashboardView.vue'),
    },
    {
      path: '/dashboard/procurement',
      name: 'procurementDashboard',
      component: () => import('@/views/ProcurementDashboardView.vue'),
    },
    {
      path: '/dashboard/production',
      name: 'productionDashboard',
      component: () => import('@/views/ProductionDashboardView.vue'),
    },
    {
      path: '/dashboard/finance',
      name: 'financeDashboard',
      component: () => import('@/views/FinanceDashBoardView.vue'),
    },
    {
      path: '/dashboard/hr',
      name: 'hrDashboard',
      component: () => import('@/views/HRDashboardView.vue'),
    },

    // ── Data pages ───────────────────────────────────────────────────
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
      path: '/customers',
      name: 'customerList',
      component: () => import('@/views/CustomerListView.vue'),
    },
    {
      path: '/customers/:id',
      name: 'customerDetail',
      component: () => import('@/views/CustomerDetailView.vue'),
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
