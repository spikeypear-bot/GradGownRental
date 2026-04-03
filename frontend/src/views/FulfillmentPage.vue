<template>
  <div class="fulfillment-container">
    <div class="container py-4">
      <div class="mb-4">
        <h2 class="fw-bold mb-2">Process Fulfillment</h2>
        <p class="text-muted">Confirmed orders ready for collection or delivery</p>
      </div>

      <!-- Search -->
      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <div class="search-box">
            <i class="bi bi-search"></i>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search by customer name or order ID"
            />
          </div>
        </div>
        <div class="col-md-6">
          <button @click="refreshOrders" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-clockwise"></i> Refresh
          </button>
        </div>
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
            <div class="card-header-section">
              <div class="d-flex align-items-center gap-2 mb-1">
                <i class="bi bi-bag-check section-icon"></i>
                <h5 class="mb-0 fw-bold">Collection</h5>
                <span class="count-badge">{{ filteredCollection.length }}</span>
              </div>
              <p class="text-muted small mb-0">Customers collecting in-store</p>
            </div>

            <div v-if="filteredCollection.length === 0" class="empty-state">
              <i class="bi bi-bag-check"></i>
              <p>No collection orders</p>
            </div>

            <div v-else class="order-list">
              <div
                v-for="order in filteredCollection"
                :key="order.order_id"
                class="order-row"
              >
                <div class="order-info">
                  <span class="order-id">{{ order.order_id.slice(0, 8) }}...</span>
                  <p class="customer-name mb-0">{{ order.student_name }}</p>
                  <small class="text-muted">
                    <i class="bi bi-calendar3 me-1"></i>
                    {{ formatDate(order.rental_start_date) }}
                  </small>
                </div>
                <button
                  class="btn btn-sm btn-collected"
                  @click="openModal(order, 'COLLECTION')"
                  :disabled="processingId === order.order_id"
                >
                  <span v-if="processingId !== order.order_id">
                    <i class="bi bi-check-lg me-1"></i>Collected
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
            <div class="card-header-section">
              <div class="d-flex align-items-center gap-2 mb-1">
                <i class="bi bi-truck section-icon"></i>
                <h5 class="mb-0 fw-bold">Delivery</h5>
                <span class="count-badge">{{ filteredDelivery.length }}</span>
              </div>
              <p class="text-muted small mb-0">Orders to be delivered to customers</p>
            </div>

            <div v-if="filteredDelivery.length === 0" class="empty-state">
              <i class="bi bi-truck"></i>
              <p>No delivery orders</p>
            </div>

            <div v-else class="order-list">
              <div
                v-for="order in filteredDelivery"
                :key="order.order_id"
                class="order-row"
              >
                <div class="order-info">
                  <span class="order-id">{{ order.order_id.slice(0, 8) }}...</span>
                  <p class="customer-name mb-0">{{ order.student_name }}</p>
                  <small class="text-muted">
                    <i class="bi bi-calendar3 me-1"></i>
                    {{ formatDate(order.rental_start_date) }}
                  </small>
                </div>
                <button
                  class="btn btn-sm btn-delivered"
                  @click="openModal(order, 'DELIVERY')"
                  :disabled="processingId === order.order_id"
                >
                  <span v-if="processingId !== order.order_id">
                    <i class="bi bi-truck me-1"></i>Delivered
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

      <!-- Confirmation Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h4 class="mb-3">
            {{ modalType === 'COLLECTION' ? 'Confirm Collection' : 'Confirm Delivery' }}
          </h4>
          <p class="text-muted">
            Mark order <strong>{{ selectedOrder?.order_id }}</strong> for
            <strong>{{ selectedOrder?.student_name }}</strong> as
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
                {{ modalType === 'COLLECTION' ? 'Collected' : 'Delivered' }}
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

const orders = ref([])
const searchQuery = ref('')
const isLoading = ref(false)
const processingId = ref(null)
const isProcessing = ref(false)
const showModal = ref(false)
const selectedOrder = ref(null)
const modalType = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

const filteredOrders = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return orders.value
  return orders.value.filter(order =>
    order.order_id?.toLowerCase().includes(query) ||
    order.student_name?.toLowerCase().includes(query) ||
    order.email?.toLowerCase().includes(query)
  )
})

const filteredCollection = computed(() =>
  filteredOrders.value.filter(o => o.fulfillment_method === 'COLLECTION')
)

const filteredDelivery = computed(() =>
  filteredOrders.value.filter(o => o.fulfillment_method === 'DELIVERY')
)

const formatDate = (dateString) => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(new Date(dateString))
  } catch {
    return dateString
  }
}

const loadConfirmedOrders = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    orders.value = await fetchOrdersByStatus(orderApiUrl, 'CONFIRMED')
  } catch (error) {
    console.error('Error loading confirmed orders:', error)
    errorMessage.value = 'Failed to load confirmed orders'
  } finally {
    isLoading.value = false
  }
}

const refreshOrders = () => loadConfirmedOrders()

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
  processingId.value = selectedOrder.value.order_id
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await AdminService.activateFulfillment(selectedOrder.value.order_id)
    successMessage.value = `Order ${selectedOrder.value.order_id.slice(0, 8)}... marked as ${modalType.value === 'COLLECTION' ? 'collected' : 'delivered'} and moved to Active Rentals.`
    orders.value = orders.value.filter(o => o.order_id !== selectedOrder.value.order_id)
    closeModal()
    setTimeout(() => { successMessage.value = '' }, 4000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to update order'
  } finally {
    isProcessing.value = false
    processingId.value = null
  }
}

onMounted(() => loadConfirmedOrders())
</script>

<style scoped>
.fulfillment-container {
  min-height: 100vh;
  background-color: #fbf7ef;
  padding-top: 100px;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.search-box {
  position: relative;
}
.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #d8a61c;
}
.search-box .form-control {
  padding-left: 2.5rem;
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  background-color: white;
}
.search-box .form-control:focus {
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
}

.btn-outline-secondary {
  border-color: #d8a61c;
  color: #d8a61c;
  border-radius: 12px;
  font-weight: 600;
}
.btn-outline-secondary:hover {
  background-color: #d8a61c;
  border-color: #d8a61c;
  color: white;
}

.fulfillment-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 100%;
}

.card-header-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0ddd3;
  margin-bottom: 1rem;
}

.section-icon {
  font-size: 1.25rem;
  color: #d8a61c;
}

.count-badge {
  margin-left: auto;
  background-color: #d8a61c;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 10px;
  font-weight: 700;
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
