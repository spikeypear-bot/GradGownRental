<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const CART_STORAGE_KEY = 'gradgownrental_cart_session'

const cartItems = ref([])
const cartExpiresAt = ref(0)
const nowMs = ref(Date.now())
let timerId = null

const cartActive = computed(() => cartExpiresAt.value > nowMs.value)
const cartSecondsLeft = computed(() => {
  if (!cartActive.value) return 0
  return Math.max(0, Math.floor((cartExpiresAt.value - nowMs.value) / 1000))
})
const cartTimeLeftLabel = computed(() => {
  const sec = cartSecondsLeft.value
  const mm = String(Math.floor(sec / 60)).padStart(2, '0')
  const ss = String(sec % 60).padStart(2, '0')
  return `${mm}:${ss}`
})
const cartTotal = computed(() => cartItems.value.reduce((sum, item) => sum + Number(item.price || 0), 0))

function loadCartSession() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY)
    if (!raw) {
      cartItems.value = []
      cartExpiresAt.value = 0
      return
    }
    const parsed = JSON.parse(raw)
    cartItems.value = Array.isArray(parsed.items) ? parsed.items : []
    cartExpiresAt.value = Number(parsed.expiresAt || 0)
  } catch {
    cartItems.value = []
    cartExpiresAt.value = 0
  }
}

function saveCartSession() {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify({
    expiresAt: cartExpiresAt.value,
    items: cartItems.value
  }))
}

function clearCartSession() {
  cartItems.value = []
  cartExpiresAt.value = 0
  localStorage.removeItem(CART_STORAGE_KEY)
}

function removeFromCart(packageId) {
  cartItems.value = cartItems.value.filter(item => (item.cartKey || item.packageId) !== packageId)
  if (!cartItems.value.length) {
    clearCartSession()
    return
  }
  saveCartSession()
}

function browsePackages() {
  router.push('/inventory?new=true')
}

function checkoutAll() {
  if (!cartActive.value) {
    clearCartSession()
    return
  }
  router.push('/order?cartCheckout=true')
}

onMounted(() => {
  loadCartSession()

  timerId = setInterval(() => {
    nowMs.value = Date.now()
    if (cartExpiresAt.value > 0 && cartExpiresAt.value <= nowMs.value) {
      clearCartSession()
    }
  }, 1000)

  window.addEventListener('storage', loadCartSession)
})

onBeforeUnmount(() => {
  if (timerId) clearInterval(timerId)
  window.removeEventListener('storage', loadCartSession)
})
</script>

<template>
  <div class="cart-page pt-5">
    <div class="container py-4 fade-in">
      <div class="d-flex justify-content-between align-items-center mb-4 mt-2">
        <h1 class="fw-bold text-dark mb-0">Your Cart</h1>
        <button class="btn btn-link text-dark text-decoration-none fw-bold" @click="browsePackages">
          <i class="bi bi-arrow-left me-2"></i>Continue Browsing
        </button>
      </div>

      <div v-if="!cartItems.length" class="bg-white rounded-4 shadow-sm p-5 text-center">
        <i class="bi bi-cart3 fs-1 text-secondary"></i>
        <h4 class="fw-bold mt-3">Your cart is empty</h4>
        <p class="text-secondary mb-4">Add a regalia package from the collections page to start checkout.</p>
        <button class="btn btn-warning text-white fw-bold rounded-pill px-4" @click="browsePackages">Browse Collections</button>
      </div>

      <div v-else>
        <div class="alert" :class="cartActive ? 'alert-warning' : 'alert-danger'" role="alert">
          <div class="d-flex justify-content-between align-items-center">
            <span class="fw-bold">
              {{ cartActive ? 'Cart Soft Reservation Window' : 'Cart Session Expired' }}
            </span>
            <span class="badge" :class="cartActive ? 'bg-warning text-dark' : 'bg-danger'">
              {{ cartTimeLeftLabel }}
            </span>
          </div>
          <div class="small mt-2" v-if="cartActive">
            Items stay in cart for 10 minutes. Complete checkout quickly to secure your order.
          </div>
          <div class="small mt-2" v-else>
            Please add items again to continue.
          </div>
        </div>

        <div class="d-flex flex-column gap-3 mb-4">
          <div v-for="item in cartItems" :key="item.cartKey || item.packageId" class="bg-white rounded-4 shadow-sm p-4 d-flex justify-content-between align-items-center gap-3">
            <div>
              <h5 class="fw-bold text-dark mb-1">{{ item.title }}</h5>
              <div class="text-secondary">{{ item.faculty }}</div>
              <div class="small text-secondary mt-1">Size: <span class="fw-bold text-dark">{{ item.selectedSize || 'N/A' }}</span></div>
              <div class="fw-bold mt-2">${{ Number(item.price).toFixed(2) }}</div>
            </div>
            <div class="d-flex flex-column gap-2 align-items-end">
              <button class="btn btn-outline-secondary" @click="removeFromCart(item.cartKey || item.packageId)">
                Remove
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-4 shadow-sm p-4 d-flex justify-content-between align-items-center">
          <span class="fw-bold fs-5">Total</span>
          <span class="fw-bold fs-4 text-dark">${{ cartTotal.toFixed(2) }}</span>
        </div>
        <div class="mt-3 d-grid">
          <button class="btn btn-warning text-white fw-bold py-3" :disabled="!cartActive || !cartItems.length" @click="checkoutAll">
            Checkout All Items
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-page {
  background-color: #fbf7ef;
  min-height: 100vh;
  padding-bottom: 5rem;
}

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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
