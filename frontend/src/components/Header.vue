<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import Logo from './icons/Logo.vue'
import AuthService from '../services/auth'

const router = useRouter()
const isAdminLoggedIn = ref(false)

function checkAdminAuth() {
  isAdminLoggedIn.value = AuthService.isAuthenticated()
}

function handleLogout() {
  AuthService.logout()
  isAdminLoggedIn.value = false
  router.push('/admin/login')
}

function handleAdminClick() {
  if (!isAdminLoggedIn.value) {
    router.push('/admin/login')
  } else {
    router.push('/admin')
  }
}

onMounted(() => {
  checkAdminAuth()
  window.addEventListener('storage', checkAdminAuth)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', checkAdminAuth)
})
</script>

<template>
  <nav class="navbar navbar-expand-md site-header fixed-top">
    <div class="container py-2">
      <!-- Brand -->
      <RouterLink class="navbar-brand d-flex align-items-center gap-2" to="/">
        <Logo width="36" height="36" />
        <span class="brand-text">GradGown</span>
      </RouterLink>

      <!-- Mobile Toggle -->
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent" aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Nav Links -->
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav mx-auto mb-2 mb-md-0 fw-medium gap-md-4 align-items-center">
          <li class="nav-item">
            <RouterLink class="nav-link fw-bold text-dark" to="/inventory?new=true">Rent Regalia</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link fw-bold text-danger-custom d-flex align-items-center gap-2" to="/track">
              <i class="bi bi-search"></i> Track My Order
            </RouterLink>
          </li>
        </ul>

        <!-- Action Buttons -->
        <div class="d-flex align-items-center gap-3 mt-3 mt-md-0">
          <button v-if="isAdminLoggedIn" @click="handleLogout" class="btn btn-outline-danger rounded-pill px-4 fw-bold">
            Logout
          </button>
          <RouterLink v-else to="/admin/login" class="btn btn-warning text-white rounded-pill px-4 fw-bold">Admin Login</RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.site-header {
  background: rgba(251, 247, 239, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.brand-text {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2b3035;
}

.text-danger-custom {
  color: #b54a2a !important;
}

.text-admin {
  color: #d8a61c !important;
}

.btn-warning {
  background-color: #d8a61c;
  border-color: #d8a61c;
  font-weight: 700;
  border-radius: 20px;
}
.btn-warning:hover {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-outline-secondary,
.btn-outline-danger {
  border-radius: 20px;
  font-weight: 600;
}

.nav-link {
  font-weight: 600;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #d8a61c !important;
}
</style>
