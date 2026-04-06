<script setup>
import { RouterView, useRouter } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import Header from './components/Header.vue'
import AdminSidebar from './components/AdminSidebar.vue'
import AuthService from './services/auth'

const router = useRouter()
const isAdminLoggedIn = ref(false)

const checkAdminAuth = () => {
  isAdminLoggedIn.value = AuthService.isAuthenticated()
}

// Show sidebar only if logged in AND on admin route
const isAdminRoute = computed(() => {
  return router.currentRoute.value.path.startsWith('/admin')
})

const showAdminSidebar = computed(() => {
  return isAdminLoggedIn.value && isAdminRoute.value
})

// Show header on non-admin routes (home, inventory, order, etc.) or when not logged in
const showHeader = computed(() => {
  return !isAdminRoute.value || !isAdminLoggedIn.value
})

onMounted(() => {
  checkAdminAuth()
  window.addEventListener('storage', checkAdminAuth)
})

// Watch for route changes to check auth status
watch(
  () => router.currentRoute.value.path,
  () => {
    checkAdminAuth()
  }
)
</script>

<template>
  <div class="app-shell" :class="{ 'admin-layout': showAdminSidebar }">
    <AdminSidebar v-if="showAdminSidebar" />
    <Header v-if="showHeader" class="app-header"/>
    <main class="app-main">
      <router-view v-slot="{ Component, route }">
        <keep-alive :include="['inventory']">
          <component :is="Component" :key="route.fullPath" />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--color-background-soft, #fbf7ef);
  display: flex;
  flex-direction: column;
}

.app-shell.admin-layout {
  margin-left: 260px;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
}

.app-main {
  flex: 1; /* fills remaining height */
}

@media (max-width: 768px) {
  .app-shell.admin-layout {
    margin-left: 0;
  }
}
</style>
  