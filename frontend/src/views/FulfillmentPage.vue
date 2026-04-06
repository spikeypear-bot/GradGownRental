<template>
  <div class="fulfillment-container">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Admin / Driver</h2>
        <p class="text-muted mb-0">Manage onsite collections and driver deliveries.</p>
        <p v-if="isDemoMode" class="text-warning mb-0 small">Demo mode is on. All confirmed orders are shown regardless of date.</p>
      </div>

      <!-- Alerts -->
      <div v-if="successMessage" class="alert alert-success mb-4" role="alert">
        <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-danger mb-4" role="alert">
        <i class="bi bi-exclamation-circle me-2"></i>{{ errorMessage }}
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading confirmed orders...</p>
      </div>

      <!-- Two columns -->
      <div v-else class="row g-4">
        <!-- Collection Column -->
        <div class="col-lg-6">
          <div class="fulfillment-card">
            <h5 class="mb-3 fw-bold">Collection for {{ activeDateLabel }}</h5>

            <div v-if="filteredCollection.length === 0" class="empty-state">
              <i class="bi bi-bag-check"></i>
              <p>No collection orders for today.</p>
            </div>

            <div v-else class="order-list">
              <div
                v-for="order in filteredCollection"
                :key="order.orderID"
                class="order-row"
              >
                <div class="order-info">
                  <span class="order-id">{{ order.orderID }}</span>
                  <p class="customer-name mb-0">{{ order.CustomerName }}</p>
                  <span class="tracking-pill tracking-not-collected">NOT COLLECTED</span>
                </div>
                <button
                  class="btn btn-sm btn-collected"
                  @click="openModal(order, 'COLLECTION')"
                  :disabled="processingId === order.orderID"
                >
                  <span v-if="processingId !== order.orderID">
                    Mark as Collected
                  </span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Updating...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Delivery Column -->
        <div class="col-lg-6">
          <div class="fulfillment-card">
            <h5 class="mb-3 fw-bold">Delivery for {{ activeDateLabel }}</h5>

            <div v-if="filteredDelivery.length === 0" class="empty-state">
              <i class="bi bi-truck"></i>
              <p>No delivery orders for today.</p>
            </div>

            <div v-else class="order-list">
              <div
                v-for="order in filteredDelivery"
                :key="order.orderID"
                class="order-row"
              >
                <div class="order-info">
                  <span class="order-id">{{ order.orderID }}</span>
                  <p class="customer-name mb-0">{{ order.CustomerName }}</p>
                  <span class="tracking-pill tracking-scheduled">SCHEDULED</span>
                </div>
                <button
                  class="btn btn-sm btn-delivered"
                  @click="openModal(order, 'DELIVERY')"
                  :disabled="processingId === order.orderID"
                >
                  <span v-if="processingId !== order.orderID">
                   Mark as Delivered
                  </span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-1"></span>
                    Updating...
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isLoading" class="row g-4 mt-1">
        <div class="col-12">
          <div class="fulfillment-card">
            <h5 class="mb-3 fw-bold">Future Delivery Overview (Confirmed / Scheduled)</h5>

            <div v-if="futureDeliveryOverview.length === 0" class="empty-state">
              <i class="bi bi-calendar-check"></i>
              <p>No upcoming delivery orders.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Customer</th>
                    <th>Rental Start</th>
                    <th>Order Status</th>
                    <th>Tracking Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="order in futureDeliveryOverview" :key="`future-${order.orderID}`">
                    <td class="fw-semibold">{{ order.orderID }}</td>
                    <td>{{ order.CustomerName || '-' }}</td>
                    <td>{{ formatDate(order.rental_start_date) }}</td>
                    <td><span class="tracking-pill tracking-confirmed">{{ order.status }}</span></td>
                    <td><span class="tracking-pill tracking-scheduled">SCHEDULED</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!isLoading" class="row g-4 mt-1">
        <div class="col-12">
          <div class="fulfillment-card">
            <h5 class="mb-3 fw-bold">Tracking for {{ activeDateLabel }}</h5>

            <div v-if="todayTrackingRows.length === 0" class="empty-state">
              <i class="bi bi-list-check"></i>
              <p>No tracked collection/delivery updates for today yet.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Customer</th>
                    <th>Fulfillment</th>
                    <th>Order Status</th>
                    <th>Tracking Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in todayTrackingRows" :key="`track-${row.orderID}`">
                    <td class="fw-semibold">{{ row.orderID }}</td>
                    <td>{{ row.CustomerName || '-' }}</td>
                    <td>{{ row.fulfillment_method || '-' }}</td>
                    <td><span class="tracking-pill tracking-active">{{ row.status || 'ACTIVE' }}</span></td>
                    <td>
                      <span
                        :class="[
                          'tracking-pill',
                          row.tracking_status === 'DELIVERED' ? 'tracking-delivered' : 'tracking-collected'
                        ]"
                      >
                        {{ row.tracking_status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Confirmation Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h4 class="mb-3">
            {{ modalType === 'COLLECTION' ? 'Confirm Collection' : 'Confirm Delivery' }}
          </h4>
          <p class="text-muted">
            Mark order <strong>{{ selectedOrder?.orderID }}</strong> for
            <strong>{{ selectedOrder?.CustomerName }}</strong> as
            {{ modalType === 'COLLECTION' ? 'collected' : 'delivered' }}?
            This will move the order to Active Rentals.
          </p>
          <div class="d-flex gap-2 justify-content-end mt-4">
            <button @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button
              @click="submitFulfillment"
              :class="modalType === 'COLLECTION' ? 'btn btn-collected' : 'btn btn-delivered'"
            >
              <span v-if="!isProcessing">
                {{ modalType === 'COLLECTION' ? 'Collect' : 'Deliver' }}
              </span>
              <span v-else>
                <span class="spinner-border spinner-border-sm me-1"></span>
                Processing...
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminService from '../services/admin'
import { fetchOrdersByStatus } from '../services/admin/helpers'
import { isDemoMode } from '../config/demoMode'

const confirmedOrders = ref([])
const activeOrders = ref([])
const isLoading = ref(false)
const processingId = ref(null)
const isProcessing = ref(false)
const showModal = ref(false)
const selectedOrder = ref(null)
const modalType = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

function formatDateKey(dateInput) {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Singapore',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
  return formatter.format(new Date(dateInput))
}

const filteredOrders = computed(() => {
  if (isDemoMode) {
    return confirmedOrders.value
  }

  const targetDate = formatDateKey(new Date())
  return confirmedOrders.value
    .filter(order => {
      if (!order.rental_start_date) return false
      return formatDateKey(order.rental_start_date) === targetDate
    })
})

const filteredCollection = computed(() =>
  filteredOrders.value.filter(o => o.fulfillment_method === 'COLLECTION')
)

const filteredDelivery = computed(() =>
  filteredOrders.value.filter(o => o.fulfillment_method === 'DELIVERY')
)

const futureDeliveryOverview = computed(() => {
  const todayKey = formatDateKey(new Date())

  return confirmedOrders.value
    .filter(order => order.fulfillment_method === 'DELIVERY')
    .filter(order => {
      if (!order.rental_start_date) return false
      const startDateKey = formatDateKey(order.rental_start_date)
      return isDemoMode ? true : startDateKey > todayKey
    })
    .sort((a, b) => new Date(a.rental_start_date) - new Date(b.rental_start_date))
})

const todayTrackingRows = computed(() => {
  const targetDate = formatDateKey(new Date())

  return activeOrders.value
    .filter(order => {
      if (!order.rental_start_date) return false
      return isDemoMode ? true : formatDateKey(order.rental_start_date) === targetDate
    })
    .map(order => ({
      ...order,
      tracking_status: order.fulfillment_method === 'DELIVERY' ? 'DELIVERED' : 'COLLECTED'
    }))
    .sort((a, b) => String(a.orderID).localeCompare(String(b.orderID)))
})

const activeDateLabel = computed(() => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(new Date())
  } catch {
    return String(new Date())
  }
})

const loadFulfillmentData = async () => {
  isLoading.value = true
  try {
    const orderApiUrl =
      import.meta.env.VITE_ORDER_API_BASE_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'
    const [confirmed, active] = await Promise.all([
      fetchOrdersByStatus(orderApiUrl, 'CONFIRMED'),
      fetchOrdersByStatus(orderApiUrl, 'ACTIVE')
    ])

    confirmedOrders.value = confirmed
    activeOrders.value = active
  } catch (error) {
    console.error('Error loading confirmed orders:', error)
    errorMessage.value = 'Failed to load fulfillment overview'
  } finally {
    isLoading.value = false
  }
}

const openModal = (order, type) => {
  selectedOrder.value = order
  modalType.value = type
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedOrder.value = null
  modalType.value = null
}

const submitFulfillment = async () => {
  isProcessing.value = true
  processingId.value = selectedOrder.value.orderID
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await AdminService.activateFulfillment(selectedOrder.value.orderID)
    successMessage.value = `Order ${selectedOrder.value.orderID} marked as ${modalType.value === 'COLLECTION' ? 'collected' : 'delivered'} and moved to Active Rentals.`
    const completedOrderId = selectedOrder.value.orderID
    const movedOrder = confirmedOrders.value.find(o => o.orderID === completedOrderId)
    confirmedOrders.value = confirmedOrders.value.filter(o => o.orderID !== completedOrderId)
    if (movedOrder) {
      activeOrders.value = [{ ...movedOrder, status: 'ACTIVE' }, ...activeOrders.value]
    }
    closeModal()
    setTimeout(() => { successMessage.value = '' }, 4000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to update order'
  } finally {
    isProcessing.value = false
    processingId.value = null
  }
}

onMounted(() => loadFulfillmentData())
</script>

<style scoped>
.fulfillment-container {
  min-height: 100vh;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.fulfillment-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: 360px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #aaa;
}
.empty-state i {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
  color: #d8a61c;
  opacity: 0.4;
}
.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.order-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background-color: #f9f7f2;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}
.order-row:hover {
  background-color: #f3eedf;
}

.order-info {
  flex: 1;
  min-width: 0;
}
.order-id {
  font-size: 0.75rem;
  font-weight: 700;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
}
.customer-name {
  font-weight: 600;
  color: #2b3035;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tracking-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  margin-top: 0.35rem;
}

.tracking-scheduled {
  background: #fff4de;
  color: #b38310;
}

.tracking-not-collected {
  background: #fdeaea;
  color: #b74141;
}

.tracking-collected {
  background: #e8f6ec;
  color: #22804a;
}

.tracking-delivered {
  background: #e9f2ff;
  color: #2757a5;
}

.tracking-confirmed {
  background: #f0f0f0;
  color: #5f5f5f;
}

.tracking-active {
  background: #e9f2ff;
  color: #2757a5;
}

.btn-collected {
  background-color: #28a745;
  border-color: #28a745;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: 0.75rem;
}
.btn-collected:hover:not(:disabled) {
  background-color: #218838;
  border-color: #218838;
  color: white;
}

.btn-delivered {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: 0.75rem;
}
.btn-delivered:hover:not(:disabled) {
  background-color: #0b5ed7;
  border-color: #0b5ed7;
  color: white;
}

.btn-collected:disabled,
.btn-delivered:disabled {
  opacity: 0.6;
}

.alert {
  border-radius: 12px;
  border: none;
}
.alert-success {
  background-color: #d1e7dd;
  color: #0f5132;
}
.alert-danger {
  background-color: #f8d7da;
  color: #842029;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}
.modal-content h4 {
  color: #2b3035;
  font-weight: 700;
}
.modal-content p {
  color: #555;
}

.btn-secondary {
  background-color: #6c757d;
  border-color: #6c757d;
  border-radius: 12px;
  font-weight: 600;
}
.btn-secondary:hover {
  background-color: #5a6268;
  border-color: #5a6268;
}

@media (max-width: 768px) {
  .order-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .btn-collected,
  .btn-delivered {
    margin-left: 0;
    width: 100%;
  }
}
</style>
