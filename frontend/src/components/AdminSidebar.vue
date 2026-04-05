<template>
  <div class="admin-sidebar">
    <div class="sidebar-header">
      <h5>Admin Panel</h5>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-section">
        <h6>Overview</h6>
        <RouterLink
          to="/admin"
          class="nav-item"
          :class="{ active: isActive('/admin', true) }"
        >
          <i class="bi bi-graph-up"></i>
          <span>View Orders</span>
        </RouterLink>
        <RouterLink
          to="/admin/stock-overview"
          class="nav-item"
          :class="{ active: isActive('/admin/stock-overview') }"
        >
          <i class="bi bi-box-seam"></i>
          <span>Stock Overview</span>
        </RouterLink>
      </div>

      <div class="nav-section">
        <h6>Fulfillment</h6>
        <RouterLink
          to="/admin/fulfillment"
          class="nav-item"
          :class="{ active: isActive('/admin/fulfillment') }"
        >
          <i class="bi bi-truck"></i>
          <span>Process Fulfillment</span>
        </RouterLink>
      </div>

      <div class="nav-section">
        <h6>Returns</h6>
        <RouterLink
          to="/admin/returns"
          class="nav-item"
          :class="{ active: isActive('/admin/returns') }"
        >
          <i class="bi bi-arrow-return-left"></i>
          <span>Process Return</span>
        </RouterLink>
        <RouterLink
          to="/admin/check-damage"
          class="nav-item"
          :class="{ active: isActive('/admin/check-damage') }"
        >
          <i class="bi bi-exclamation-triangle"></i>
          <span>Check Damage</span>
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
import { useRouter, useRoute } from 'vue-router'
import AuthService from '../services/auth'

const router = useRouter()
const route = useRoute()

const isActive = (path, exact = false) => {
  return exact
    ? route.path === path
    : route.path === path || route.path.startsWith(path + '/')
}

const logout = () => {
  AuthService.logout()
  router.push('/admin/login')
}

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
  padding-top: 0;
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
