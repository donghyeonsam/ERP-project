import { createRouter, createWebHistory } from 'vue-router'
import MainPageView from '@/views/MainPageView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import ArticleListView from '@/views/ArticleListView.vue'
import CalendarView from '@/views/CalendarView.vue'
import CustomerListView from '@/views/CustomerListView.vue'
import CustomerDetailView from '@/views/CustomerDetailView.vue'
import EmployeeDetailView from '@/views/EmployeeDetailView.vue'
import EmployeesListView from '@/views/EmployeesListView.vue'
import WorkDetailView from '@/views/WorkDetailView.vue'
import WorkListView from '@/views/WorkListView.vue'
import WorkFlowView from '@/views/WorkFlowView.vue'
import FinanceDashBoardView from '@/views/FinanceDashBoardView.vue'
import ManagementDashBoardView from '@/views/ManagementDashBoardView.vue'
import WorkCreateView from '@/views/WorkCreateView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainPageView,
    },
    {
      path: '/articles',
      name: 'articleList',
      component: ArticleListView,
    },
    {
      path: '/articles/:id',
      name: 'articleDetail',
      component: ArticleDetailView,
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: CalendarView,
    },
    {
      path: '/customers',
      name: 'customerList',
      component: CustomerListView,
    },
    {
      path: '/customers/:id',
      name: 'customerDetail',
      component: CustomerDetailView,
    },
    {
      path: '/employees',
      name: 'employeeList',
      component: EmployeesListView,
    },
    {
      path: '/employees/:id',
      name: 'employeeDetail',
      component: EmployeeDetailView,
    },
    {
      path: '/financeDashboard',
      name: 'financeDashboard',
      component: FinanceDashBoardView,
    },
    {
      path: '/managementDashboard',
      name: 'managementDashboard',
      component: ManagementDashBoardView,
    },
    {
      path: '/works',
      name: 'workList',
      component: WorkListView,
    },
    {
      path: '/works/:id',
      name: 'workDetail',
      component: WorkDetailView,
    },
    {
      path: '/workFlow',
      name: 'workFlow',
      component: WorkFlowView,
    },
    {
      path: '/workCreate',
      name: 'workCreate',
      component: WorkCreateView,
    },
  ],
})

export default router
