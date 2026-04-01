<template>
  <nav class="navbar navbar-expand-md admin-header fixed-top">
    <div class="container-fluid py-3 px-4">
      <!-- Admin Dashboard Title -->
      <div class="admin-title d-flex align-items-center gap-3">
        <div class="admin-logo">
          <i class="bi bi-shield-check"></i>
        </div>
        <div>
          <h4 class="mb-0 fw-bold">Admin Dashboard</h4>
          <small class="text-muted">Gown Rental Management</small>
        </div>
      </div>

      <!-- Mobile Toggle -->
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#adminNavContent" aria-controls="adminNavContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Admin Nav Links -->
      <div class="collapse navbar-collapse ms-auto" id="adminNavContent">
        <ul class="navbar-nav ms-auto mb-2 mb-md-0 fw-medium gap-md-3 align-items-center">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin" :class="isActive('/admin') && route.path === '/admin' ? 'active' : ''">
              <i class="bi bi-speedometer2"></i> Overview
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/fulfillment" :class="isActive('/admin/fulfillment')">
              <i class="bi bi-truck"></i> Fulfillment
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/returns" :class="isActive('/admin/returns')">
              <i class="bi bi-arrow-clockwise"></i> Returns
            </RouterLink>
          </li>
        </ul>

        <!-- Logout Button -->
        <div class="d-flex align-items-center gap-2 mt-3 mt-md-0 ms-md-3">
          <button @click="handleLogout" class="btn btn-outline-danger btn-sm fw-bold">
            <i class="bi bi-box-arrow-right"></i> Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import AuthService from '../services/auth'

const router = useRouter()
const route = useRoute()

const handleLogout = () => {
  AuthService.logout()
  router.push('/admin/login')
}

const isActive = (path) => {
  return route.path.startsWith(path) ? 'active' : ''
}
</script>

<style scoped>
.admin-header {
  background: white;
  border-bottom: 2px solid #d8a61c;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.admin-title {
  min-width: fit-content;
}

.admin-logo {
  width: 45px;
  height: 45px;
  background-color: #d8a61c;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.3rem;
}

.admin-title h4 {
  color: #2b3035;
  font-size: 1.3rem;
  letter-spacing: 0.5px;
}

.admin-title small {
  font-size: 0.8rem;
  display: block;
}

.nav-link {
  color: #6c757d !important;
  font-weight: 600;
  border-radius: 8px;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.nav-link i {
  font-size: 1.1rem;
}

.nav-link:hover,
.nav-link.active {
  color: #d8a61c !important;
  background-color: #f6efe1;
}

.nav-link.active {
  font-weight: 700;
}

.btn-outline-danger {
  border-radius: 12px;
  font-weight: 700;
  border-color: #dc3545;
  color: #dc3545;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}
</style>
