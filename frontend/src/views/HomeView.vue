<template>
  <section class="home-hero d-flex align-items-start">
    <div class="container hero-content">
      <h1 class="hero-title text-white">
        A Moment of<br />
        <span class="achievement-text">Achievement.</span>
      </h1>

      <p class="hero-subtitle mt-4 mb-5 max-w-740">
        Premium academic regalia rentals with professional cleaning and seamless guest checkout.
      </p>

      <div class="d-flex flex-wrap gap-4 align-items-center mt-3">
        <RouterLink to="/inventory?new=true" class="btn btn-rent rounded-pill px-5 py-3 fw-bold fs-5 shadow-sm">Rent Your Gown</RouterLink>
        
        <div class="track-input-wrapper position-relative">
          <i class="bi bi-search track-icon"></i>
          <input type="text" class="form-control rounded-pill track-input" placeholder="Enter Order ID to Track...">
          <button class="btn bg-white text-warning-custom rounded-pill fw-bold track-btn">Track</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.home-hero {
  position: relative;
  min-height: 100vh;
  width: 100%;
  background-color: #dfa81e; /* golden yellow */
  padding-top: 180px; /* shift text up closer to header */
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-title {
  font-size: clamp(4rem, 9vw, 6.5rem);
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.achievement-text {
  position: relative;
  display: inline-block;
  color: #ffffff;
  z-index: 1;
}

.achievement-text::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 12px;
  background-color: #b54a2a;
  z-index: -1;
}

.text-warning-custom {
  color: #dfa81e !important;
}

.hero-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: clamp(1.2rem, 2vw, 1.5rem);
  line-height: 1.4;
  font-weight: 400;
}

.max-w-740 {
  max-width: 650px;
}

.btn-rent {
  background-color: #b54a2a;
  color: white;
  border: none;
  transition: all 0.2s ease;
}

.btn-rent:hover {
  background-color: #9d3d20;
  color: white;
  transform: translateY(-2px);
}

.track-input-wrapper {
  width: 450px;
  max-width: 100%;
}

.track-input {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 1rem 1rem 1rem 3rem;
  font-size: 1.05rem;
}

.track-input::placeholder {
  color: rgba(255, 255, 255, 0.8);
}

.track-input:focus {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: none;
  color: white;
}

.track-icon {
  position: absolute;
  left: 1.2rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.track-btn {
  position: absolute;
  right: 0.4rem;
  top: 50%;
  transform: translateY(-50%);
  color: #dfa81e;
  padding: 0.5rem 1.5rem;
  font-size: 0.9rem;
}

.track-btn:hover {
  background-color: #f8f9fa;
  color: #c49416 !important;
}
</style>
