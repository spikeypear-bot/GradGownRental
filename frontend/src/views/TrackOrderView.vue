<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import orderService from '@/services/order'
import inventoryService from '@/services/inventory'

const route = useRoute()
const orderId = ref((route.query.orderId || '').toString())
const loading = ref(false)
const actionLoading = ref(false)
const error = ref('')
const success = ref('')
const order = ref(null)
const packageDetail = ref(null)

// Status steps
const STATUS_STEPS = [
  { key: 'CONFIRMED',  label: 'Confirmed',     icon: 'bi-check-circle' },
  { key: 'ACTIVE',     label: 'In Possession',  icon: 'bi-box-seam' },
  { key: 'RETURNED',   label: 'Returned',       icon: 'bi-arrow-counterclockwise' },
  { key: 'COMPLETED',  label: 'Processed',      icon: 'bi-shield-check' },
]

const currentStepIndex = computed(() => {
  const status = order.value?.status
  const map = {
    PENDING: -1,
    CONFIRMED: 0,
    ACTIVE: 1,
    RETURNED_PENDING_INSPECTION: 2,
    RETURNED_DAMAGED: 2,
    COMPLETED: 3,
  }
  return map[status] ?? -1
})

const canActivate = computed(() =>
  order.value?.status === 'CONFIRMED' && order.value?.fulfillment_method === 'COLLECTION'
)

const selectedItems = computed(() =>
  Array.isArray(order.value?.selected_items) ? order.value.selected_items : []
)

const packageTitle = computed(() => {
  if (!packageDetail.value) return ''
  const parts = [packageDetail.value.institution, packageDetail.value.educationLevel].filter(Boolean)
  return parts.join(' — ')
})

const gownItem = computed(() =>
  selectedItems.value.find(i => i.itemType === 'gown') || selectedItems.value[0]
)

const trackOrder = async () => {
  if (!orderId.value.trim()) { error.value = 'Please enter an order ID.'; return }
  loading.value = true
  error.value = ''
  success.value = ''
  order.value = null
  packageDetail.value = null
  try {
    order.value = await orderService.getOrder(orderId.value.trim())
    if (order.value?.package_id)
      packageDetail.value = await inventoryService.getPackageById(order.value.package_id)
  } catch (err) {
    error.value = err.message || 'Unable to fetch order.'
  } finally {
    loading.value = false
  }
}

const activateOrder = async () => {
  if (!order.value?.order_id) return
  actionLoading.value = true
  error.value = ''
  success.value = ''
  try {
    order.value = await orderService.activateOrder(order.value.order_id)
    success.value = `Order ${order.value.order_id} is now ACTIVE.`
  } catch (err) {
    error.value = err.message || 'Unable to activate order.'
  } finally {
    actionLoading.value = false
  }
}

if (orderId.value.trim()) trackOrder()

function formatDate(value) {
  if (!value) return '-'
  const parsed = new Date(value)
  if (isNaN(parsed.getTime())) return value
  const day = parsed.getDate()
  const suffix = ['th','st','nd','rd'][(day % 10 < 4 && (day < 11 || day > 13)) ? day % 10 : 0]
  return parsed.toLocaleDateString('en-US', {
    weekday: 'long', month: 'short', day: 'numeric', year: 'numeric'
  }).replace(/(\d+)/, `$1${suffix}`)
}

function shortDate(value) {
  if (!value) return '-'
  const parsed = new Date(value)
  if (isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function maintenanceEnd(returnDate) {
  if (!returnDate) return '-'
  const d = new Date(returnDate)
  if (isNaN(d.getTime())) return '-'
  d.setDate(d.getDate() + 4)
  return shortDate(d.toISOString())
}

const statusLabel = computed(() => {
  const map = {
    PENDING: 'Pending',
    CONFIRMED: 'Confirmed',
    ACTIVE: 'Active',
    RETURNED_PENDING_INSPECTION: 'Returned',
    RETURNED_DAMAGED: 'Returned (Damaged)',
    COMPLETED: 'Processed',
  }
  return map[order.value?.status] || order.value?.status || ''
})

const sizeLabel = computed(() => {
  const item = gownItem.value || selectedItems.value[0]
  if (!item) return '-'
  return item.size ? `Standard ${item.size}` : '-'
})

const depositStatus = computed(() => {
  const amt = Number(order.value?.deposit || 0).toFixed(2)
  return `$${amt} Authorized`
})
</script>

<template>
  <section class="track-page py-5">
    <div class="container" style="max-width: 860px;">

      <!-- Search bar -->
      <div class="search-card mb-4">
        <div class="d-flex gap-2">
          <div class="search-input-wrap flex-grow-1">
            <i class="bi bi-search search-icon"></i>
            <input
              v-model="orderId"
              class="form-control search-input"
              placeholder="GG-SAMPLE"
              @keyup.enter="trackOrder"
            />
          </div>
          <button class="btn btn-lookup fw-bold px-4" :disabled="loading" @click="trackOrder">
            {{ loading ? 'Loading...' : 'Lookup' }}
          </button>
        </div>
        <p class="text-muted small mt-2 mb-0 text-center">Find your ID in the confirmation email sent after booking.</p>
      </div>

      <div v-if="error" class="alert alert-danger rounded-3">{{ error }}</div>
      <div v-if="success" class="alert alert-success rounded-3">{{ success }}</div>

      <!-- Order card -->
      <div v-if="order" class="order-card mb-3">
        <!-- Header -->
        <div class="d-flex align-items-center justify-content-between mb-3">
          <div class="d-flex align-items-center gap-3">
            <div class="pkg-icon">
              <i class="bi bi-box-seam"></i>
            </div>
            <div>
              <h5 class="fw-bold mb-0">{{ packageTitle || 'Graduation Package' }}</h5>
              <div class="text-muted small">ORDER ID: {{ order.order_id }}</div>
            </div>
          </div>
          <span class="status-badge">{{ statusLabel }}</span>
        </div>

        <!-- Status stepper -->
        <div class="stepper mb-2">
          <div
            v-for="(step, i) in STATUS_STEPS"
            :key="step.key"
            class="step-item"
          >
            <!-- Connector line before (not on first) -->
            <div v-if="i > 0" class="step-line" :class="{ active: currentStepIndex >= i }"></div>
            <div class="step-circle" :class="{ active: currentStepIndex === i, done: currentStepIndex > i }">
              <i :class="['bi', step.icon]"></i>
            </div>
            <div class="step-label" :class="{ active: currentStepIndex === i }">{{ step.label }}</div>
          </div>
        </div>
      </div>

      <!-- Bottom two cards -->
      <div v-if="order" class="row g-3 mb-3">
        <!-- Rental Timeline -->
        <div class="col-md-6">
          <div class="info-card h-100">
            <div class="d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-calendar3 text-warning"></i>
              <span class="fw-bold">Rental Timeline</span>
            </div>
            <div class="timeline-item mb-3">
              <div class="timeline-label">PICKUP / HANDOVER DATE</div>
              <div class="timeline-date">{{ formatDate(order.rental_start_date) }}</div>
            </div>
            <div class="timeline-item mb-3">
              <div class="timeline-label text-danger">RETURN DEADLINE</div>
              <div class="timeline-date">{{ formatDate(order.rental_end_date) }}</div>
            </div>
            <div class="maintenance-notice">
              <i class="bi bi-shield-exclamation me-2 text-warning"></i>
              <span class="small text-secondary">
                Mandatory sanitization: Your unit will be professionally cleaned and unavailable until
                <strong>{{ maintenanceEnd(order.rental_end_date) }}</strong>.
              </span>
            </div>
          </div>
        </div>

        <!-- Order Logistics -->
        <div class="col-md-6">
          <div class="info-card h-100">
            <div class="d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-geo-alt text-warning"></i>
              <span class="fw-bold">Order Logistics</span>
            </div>
            <div class="logistics-row">
              <span class="logistics-label">Fulfillment</span>
              <span class="logistics-pill">
                <i :class="['bi', order.fulfillment_method === 'DELIVERY' ? 'bi-truck' : 'bi-bag-check']"></i>
                {{ order.fulfillment_method === 'DELIVERY' ? 'Delivery' : 'Pickup' }}
              </span>
            </div>
            <div class="logistics-divider"></div>
            <div class="logistics-row">
              <span class="logistics-label">Size</span>
              <span class="logistics-value fw-bold">{{ sizeLabel }}</span>
            </div>
            <div class="logistics-divider"></div>
            <div class="logistics-row">
              <span class="logistics-label">Deposit Status</span>
              <span class="logistics-value text-success fw-bold">{{ depositStatus }}</span>
            </div>
            <div class="late-notice mt-3">
              <i class="bi bi-info-circle me-1"></i>
              <span class="small text-muted">Late returns incur automatic deposit forfeiture.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div v-if="order" class="d-flex gap-3 flex-wrap mb-4">
        <button class="btn btn-inquiry" @click="error = 'Submit inquiry feature coming soon.'">
          <i class="bi bi-question-circle me-2"></i>Submit Inquiry
        </button>
        <button class="btn btn-download fw-bold">
          Download PDF Receipt <i class="bi bi-arrow-right ms-1"></i>
        </button>
      </div>

      <!-- Activate (collection only) -->
      <div v-if="order && canActivate" class="info-card mb-3">
        <h6 class="fw-bold mb-2">Confirm Collection</h6>
        <p class="text-muted small mb-3">Mark this order as collected to activate the rental period.</p>
        <button class="btn btn-lookup fw-bold" :disabled="actionLoading" @click="activateOrder">
          {{ actionLoading ? 'Activating...' : 'Mark as Collected' }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.track-page {
  background-color: #f5f0e8;
  min-height: calc(100vh - 84px);
}

/* Search */
.search-card {
  background: transparent;
}
.search-input-wrap {
  position: relative;
}
.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
  font-size: 1rem;
}
.search-input {
  padding-left: 2.5rem;
  border-radius: 12px;
  border: 1.5px solid #ddd;
  background: white;
  height: 48px;
  font-size: 1rem;
}
.search-input:focus {
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.12);
}
.btn-lookup {
  background-color: #d8a61c;
  color: white;
  border: none;
  border-radius: 12px;
  height: 48px;
  font-size: 1rem;
}
.btn-lookup:hover:not(:disabled) {
  background-color: #c49416;
  color: white;
}
.btn-lookup:disabled { opacity: 0.6; }

/* Order card */
.order-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

.pkg-icon {
  width: 52px;
  height: 52px;
  background: #fff8e6;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #d8a61c;
}

.status-badge {
  background-color: #d8a61c;
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Stepper */
.stepper {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
  padding-top: 0.5rem;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}
.step-line {
  position: absolute;
  top: 20px;
  right: 50%;
  left: -50%;
  height: 2px;
  background: #e0ddd3;
  z-index: 0;
}
.step-line.active {
  background: #d8a61c;
}
.step-circle {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid #ddd;
  background: white;
  color: #bbb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  position: relative;
  z-index: 1;
  transition: all 0.2s ease;
}
.step-circle.active {
  border-color: #d8a61c;
  background: #d8a61c;
  color: white;
  box-shadow: 0 0 0 4px rgba(216, 166, 28, 0.15);
}
.step-circle.done {
  border-color: #c49416;
  background: #fff8e6;
  color: #d8a61c;
}
.step-label {
  font-size: 0.72rem;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 0.5rem;
  text-align: center;
  font-weight: 600;
}
.step-label.active {
  color: #d8a61c;
}

/* Info cards */
.info-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

/* Timeline */
.timeline-item {
  border-left: 3px solid #d8a61c;
  padding-left: 0.75rem;
}
.timeline-item:nth-child(3) {
  border-left-color: #dc3545;
}
.timeline-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #d8a61c;
  margin-bottom: 0.15rem;
}
.timeline-item:nth-child(3) .timeline-label {
  color: #dc3545;
}
.timeline-date {
  font-size: 1rem;
  font-weight: 700;
  color: #2b3035;
}
.maintenance-notice {
  background: #fff8e6;
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
}

/* Logistics */
.logistics-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0;
}
.logistics-label {
  color: #666;
  font-size: 0.95rem;
}
.logistics-value {
  font-size: 0.95rem;
  color: #2b3035;
}
.logistics-divider {
  height: 1px;
  background: #f0ede6;
}
.logistics-pill {
  background: #fff3cd;
  color: #856404;
  border-radius: 20px;
  padding: 0.25rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.late-notice {
  background: #f9f7f2;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
}

/* Action buttons */
.btn-inquiry {
  border: 1.5px solid #d8a61c;
  color: #d8a61c;
  background: white;
  border-radius: 24px;
  padding: 0.65rem 1.5rem;
  font-weight: 600;
}
.btn-inquiry:hover {
  background: #fff8e6;
}
.btn-download {
  background: #d8a61c;
  color: white;
  border: none;
  border-radius: 24px;
  padding: 0.65rem 1.5rem;
  font-size: 0.95rem;
}
.btn-download:hover {
  background: #c49416;
  color: white;
}

@media (max-width: 576px) {
  .step-label { font-size: 0.62rem; }
  .step-circle { width: 34px; height: 34px; font-size: 0.9rem; }
}
</style>