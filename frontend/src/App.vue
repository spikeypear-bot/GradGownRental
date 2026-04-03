<script setup>
import { RouterView, useRouter } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import Header from './components/Header.vue'
import AdminSidebar from './components/AdminSidebar.vue'
import AuthService from './services/auth'

const router = useRouter()
const isAdminLoggedIn = ref(false)

const checkAdminAuth = () => {
  isAdminLoggedIn.value = AuthService.isAuthenticated()
}

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

// We can intercept nav changes and explicitly clear keep-alive cache by forcing an unmount, or 
// use a dynamic key on the router view
</script>

<template>
  <div class="app-shell" :class="{ 'admin-layout': isAdminLoggedIn }">
    <AdminSidebar v-if="isAdminLoggedIn" />
    <Header v-if="!isAdminLoggedIn" class="app-header"/>
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
  