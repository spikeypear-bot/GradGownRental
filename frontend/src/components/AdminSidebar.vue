<template>
  <div class="admin-sidebar">
    <div class="sidebar-header">
      <h5>Admin Panel</h5>
      <button @click="toggleSidebar" class="btn-toggle d-lg-none">
        <i class="bi bi-x"></i>
      </button>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        to="/admin"
        class="nav-item"
        :class="{ active: isActive('/admin') }"
      >
        <i class="bi bi-graph-up"></i>
        <span>Overview</span>
      </RouterLink>

      <div class="nav-section">
        <h6>Fulfillment</h6>
        <RouterLink
          to="/admin/pending-orders"
          class="nav-item"
          :class="{ active: isActive('/admin/pending-orders') }"
        >
          <i class="bi bi-truck"></i>
          <span>Process Fulfillment</span>
          <span v-if="confirmedCount > 0" class="badge">{{ confirmedCount }}</span>
        </RouterLink>
      </div>

      <div class="nav-section">
        <h6>Returns</h6>
        <RouterLink
          to="/admin/returns"
          class="nav-item"
          :class="{ active: isActive('/admin/returns') }"
        >
          <i class="bi bi-arrow-clockwise"></i>
          <span>Process Return</span>
        </RouterLink>
        <RouterLink
          to="/admin/repair"
          class="nav-item"
          :class="{ active: isActive('/admin/repair') }"
        >
          <i class="bi bi-tools"></i>
          <span>Repair</span>
        </RouterLink>
        <RouterLink
          to="/admin/laundry"
          class="nav-item"
          :class="{ active: isActive('/admin/laundry') }"
        >
          <i class="bi bi-droplet-half"></i>
          <span>Laundry</span>
        </RouterLink>
      </div>
    </nav>

    <div class="sidebar-footer">
      <button @click="logout" class="btn btn-sm btn-outline-danger w-100">
        <i class="bi bi-box-arrow-right"></i>
        Logout
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AuthService from '../services/auth'

const router = useRouter()
const route = useRoute()

const pendingCount = ref(0)
const confirmedCount = ref(0)

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const logout = () => {
  AuthService.logout()
  router.push('/admin/login')
}

// In a real app, fetch these counts from the API
const loadCounts = async () => {
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    const pendingRes = await fetch(`${orderApiUrl}/orders/status/PENDING`)
    const confirmedRes = await fetch(`${orderApiUrl}/orders/status/CONFIRMED`)

    if (pendingRes.ok) {
      const data = await pendingRes.json()
      pendingCount.value = Array.isArray(data) ? data.length : 0
    }
    if (confirmedRes.ok) {
      const data = await confirmedRes.json()
      confirmedCount.value = Array.isArray(data) ? data.length : 0 // Confirmed orders ready for return processing later
    }
  } catch (error) {
    console.error('Error loading order counts:', error)
  }
}

loadCounts()
// Refresh counts every 30 seconds
setInterval(loadCounts, 30000)
</script>

<style scoped>
.admin-sidebar {
  background-color: white;
  border-right: 1px solid #e0ddd3;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  width: 260px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding-top: 80px;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e0ddd3;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h5 {
  margin: 0;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.25rem;
}

.btn-toggle {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #d8a61c;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-section {
  margin-bottom: 1.5rem;
}

.nav-section h6 {
  padding: 0.5rem 1.5rem;
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #6c757d;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: #555;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.95rem;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: #f9f7f2;
  color: #d8a61c;
}

.nav-item.active {
  background-color: #fff0da;
  color: #d8a61c;
  border-left-color: #d8a61c;
}

.nav-item i {
  width: 20px;
  text-align: center;
}

.badge {
  margin-left: auto;
  background-color: #d8a61c;
  color: white;
  font-size: 0.7rem;
  padding: 0.3rem 0.6rem;
  border-radius: 10px;
  font-weight: 700;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid #e0ddd3;
}

@media (max-width: 991px) {
  .admin-sidebar {
    width: 230px;
  }
}

@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }

  .admin-sidebar.show {
    transform: translateX(0);
  }
}
</style>
