import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AuthService from '../services/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/inventory',
      name: 'inventory',
      component: () => import('../views/InventoryView.vue')
    },
    {
      path: '/order',
      name: 'order',
      component: () => import('../views/OrderView.vue')
    },
    {
      path: '/track',
      name: 'track',
      component: () => import('../views/TrackOrderView.vue')
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/AdminLoginPage.vue')
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: () => import('../views/AdminDashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/fulfillment',
      name: 'admin-fulfillment',
      component: () => import('../views/FulfillmentPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/stock-overview',
      name: 'admin-stock-overview',
      component: () => import('../views/StockOverviewPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/fulfillment-overview',
      name: 'admin-fulfillment-overview',
      component: () => import('../views/FulfillmentOverviewPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/returns',
      name: 'admin-returns',
      component: () => import('../views/ReturnPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/repair',
      name: 'admin-repair',
      component: () => import('../views/RepairPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/laundry',
      name: 'admin-laundry',
      component: () => import('../views/LaundryPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/orders',
      name: 'admin-all-orders',
      component: () => import('../views/AdminDashboard.vue'),
      meta: { requiresAuth: true }
    }
  ],
})

// Route guard to protect admin routes
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !AuthService.isAuthenticated()) {
    // Redirect to login if trying to access protected route without auth
    next('/admin/login')
  } else if (to.path === '/admin/login' && AuthService.isAuthenticated()) {
    // Redirect to dashboard if already logged in and trying to access login
    next('/admin')
  } else {
    next()
  }
})

export default router
