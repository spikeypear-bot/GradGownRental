<template>
  <div class="active-orders-container">
    <div class="container py-4">
      <div class="mb-4">
        <h2 class="fw-bold mb-2">Active Rentals</h2>
        <p class="text-muted">Gowns currently rented out by customers</p>
      </div>

      <!-- Filters -->
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

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading active rentals...</p>
      </div>

      <!-- Table -->
      <div v-else class="orders-card">
        <div v-if="filteredOrders.length === 0" class="text-center py-5">
          <i class="bi bi-bag-check" style="font-size: 3rem; color: #d8a61c;"></i>
          <p class="mt-3 text-muted">No active rentals</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Fulfillment</th>
                <th>Rental Start</th>
                <th>Expected Return</th>
                <th>Days Remaining</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.order_id">
                <td>
                  <span class="badge bg-light text-dark">{{ order.order_id.slice(0, 8) }}...</span>
                </td>
                <td>
                  <div class="customer-info">
                    <p class="mb-0 fw-500">{{ order.student_name }}</p>
                    <small class="text-muted">{{ order.email }}</small>
                  </div>
                </td>
                <td>
                  <span :class="['method-badge', order.fulfillment_method === 'DELIVERY' ? 'method-delivery' : 'method-collection']">
                    <i :class="order.fulfillment_method === 'DELIVERY' ? 'bi bi-truck' : 'bi bi-bag-check'"></i>
                    {{ order.fulfillment_method }}
                  </span>
                </td>
                <td>{{ formatDate(order.rental_start_date) }}</td>
                <td>{{ formatDate(order.rental_end_date) }}</td>
                <td>
                  <span :class="['badge', getDaysRemainingClass(order.rental_end_date)]">
                    {{ getDaysRemaining(order.rental_end_date) }} days
                  </span>
                </td>
                <td class="fw-bold">SGD ${{ order.total_amount }}</td>
                <td>
                  <button
                    @click="markForReturn(order.order_id)"
                    class="btn btn-sm btn-warning"
                    :disabled="processingId === order.order_id"
                  >
                    <span v-if="processingId !== order.order_id">
                      <i class="bi bi-arrow-clockwise"></i> Return
                    </span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Processing...
                    </span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h4 class="mb-3">Mark for Return</h4>
          <p class="text-muted">
            Mark order <strong>{{ selectedOrderId }}</strong> for return processing?
            The customer will be notified to return the gown.
          </p>
          <div class="d-flex gap-2 justify-content-end mt-4">
            <button @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button @click="submitReturn" class="btn btn-warning">
              <span v-if="!isProcessing">Mark for Return</span>
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
const showModal = ref(false)
const selectedOrderId = ref(null)
const processingId = ref(null)
const isProcessing = ref(false)

const filteredOrders = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return orders.value
  return orders.value.filter(order =>
    order.order_id?.toLowerCase().includes(query) ||
    order.student_name?.toLowerCase().includes(query) ||
    order.email?.toLowerCase().includes(query)
  )
})

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

const getDaysRemaining = (endDate) => {
  const diffDays = Math.ceil((new Date(endDate) - new Date()) / (1000 * 60 * 60 * 24))
  return Math.max(0, diffDays)
}

const getDaysRemainingClass = (endDate) => {
  const days = getDaysRemaining(endDate)
  if (days <= 0) return 'bg-danger text-white'
  if (days <= 3) return 'bg-warning text-dark'
  return 'bg-info text-white'
}

const loadActiveOrders = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    orders.value = await fetchOrdersByStatus(orderApiUrl, 'ACTIVE')
  } catch (error) {
    console.error('Error loading active orders:', error)
  } finally {
    isLoading.value = false
  }
}

const refreshOrders = () => loadActiveOrders()

const markForReturn = (orderId) => {
  selectedOrderId.value = orderId
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedOrderId.value = null
}

const submitReturn = async () => {
  isProcessing.value = true
  processingId.value = selectedOrderId.value
  try {
    await AdminService.markForReturn(selectedOrderId.value)
    orders.value = orders.value.filter(order => order.order_id !== selectedOrderId.value)
    closeModal()
  } catch (error) {
    console.error('Error marking order for return:', error)
    alert('Failed to mark order for return: ' + error.message)
  } finally {
    isProcessing.value = false
    processingId.value = null
  }
}

onMounted(() => loadActiveOrders())
</script>

<style scoped>
.active-orders-container {
  min-height: 100vh;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
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

.orders-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
}

.table { margin: 0; border-collapse: collapse; }
.table thead th {
  background-color: #f9f7f2;
  border: none;
  padding: 1rem;
  font-weight: 700;
  color: #2b3035;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.table tbody tr:hover { background-color: #faf9f7; }
.table tbody td {
  padding: 1rem;
  border-bottom: 1px solid #e0ddd3;
  vertical-align: middle;
}
.table tbody tr:last-child td { border-bottom: none; }

.badge {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-block;
}

.method-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}
.method-collection {
  background-color: #fff3cd;
  color: #856404;
}
.method-delivery {
  background-color: #cfe2ff;
  color: #084298;
}

.customer-info p { font-size: 0.95rem; }

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
  border-radius: 8px;
  font-weight: 600;
}
.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
  border-color: #e0a800;
}
.btn-warning:disabled { opacity: 0.6; }

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
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}
.modal-content h4 { color: #2b3035; font-weight: 700; }
.modal-content p { color: #555; margin-bottom: 1rem; }

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
  .table { font-size: 0.85rem; }
  .table td, .table th { padding: 0.75rem; }
  .customer-info small { display: none; }
}
</style>