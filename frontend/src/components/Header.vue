<script setup>
import Logo from './icons/Logo.vue'
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
            <a class="nav-link fw-bold text-danger-custom d-flex align-items-center gap-2" href="#">
              <i class="bi bi-search"></i> Track My Order
            </a>
          </li>
        </ul>

        <!-- Action Buttons -->
        <div class="d-flex align-items-center gap-3 mt-3 mt-md-0">
          <RouterLink to="/inventory?new=true" class="btn btn-warning text-white rounded-pill px-4 fw-bold">Start Booking</RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.site-header {
  background: rgba(251, 247, 239, 0.85); /* translucent */
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.brand-text {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2b2b2b;
}

.text-danger-custom {
  color: #b54a2a !important;
}

.btn-warning {
  background-color: #d8a61c;
  border-color: #d8a61c;
}
.btn-warning:hover {
  background-color: #c49416;
  border-color: #c49416;
}
</style>