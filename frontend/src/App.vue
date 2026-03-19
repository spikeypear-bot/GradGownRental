<script setup>
import { RouterView, useRouter } from 'vue-router'
import Header from './components/Header.vue'

const router = useRouter()

// We can intercept nav changes and explicitly clear keep-alive cache by forcing an unmount, or 
// use a dynamic key on the router view
</script>

<template>
  <div class="app-shell">
    <Header class="app-header"/>
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

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
}

.app-main {
  flex: 1; /* fills remaining height */
}
</style>
