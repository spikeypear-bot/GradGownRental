<template>
  <div class="returns-queue-container">
    <div class="container py-4">
      <div class="mb-4">
        <h2 class="fw-bold mb-2">Returns Queue</h2>
        <p class="text-muted">Gowns returned by customers awaiting inspection and processing</p>
      </div>

      <!-- Filters and Actions -->
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

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading returns queue...</p>
      </div>

      <!-- Orders Table -->
      <div v-else class="orders-card">
        <div v-if="filteredOrders.length === 0" class="text-center py-5">
          <i class="bi bi-inbox" style="font-size: 3rem; color: #d8a61c;"></i>
          <p class="mt-3 text-muted">No returned items pending processing</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Gown</th>
                <th>Returned Date</th>
                <th>Damage Status</th>
                <th>Issue</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.orderID">
                <td>
                  <span class="badge bg-light text-dark">{{ order.orderID }}</span>
                </td>
                <td>
                  <div class="customer-info">
                    <p class="mb-0 fw-500">{{ order.CustomerName }}</p>
                    <small class="text-muted">{{ order.CustomerEmail }}</small>
                  </div>
                </td>
                <td>
                  <span class="gown-name">{{ order.GownName }}</span>
                </td>
                <td>{{ formatDate(order.returned_at) }}</td>
                <td>
                  <span :class="['badge', getDamageClass(order.damage_status)]">
                    {{ getDamageLabel(order.damage_status) }}
                  </span>
                </td>
                <td>
                  <span v-if="order.damage_to_item" class="damage-note">
                    <i class="bi bi-exclamation-circle"></i>
                    {{ order.damage_to_item }}
                  </span>
                  <span v-else class="text-muted">No damage noted</span>
                </td>
                <td>
                  <button 
                    @click="processRepair(order.orderID)"
                    class="btn btn-sm btn-primary"
                    :disabled="processingId === order.orderID"
                  >
                    <span v-if="processingId !== order.orderID">
                      <i class="bi bi-tools"></i> Process
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

      <!-- Process Return Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h4 class="mb-3">Process Return</h4>
          <div class="mb-3">
            <label class="form-label">Resolution Action</label>
            <select v-model="repairAction" class="form-select">
              <option value="">Select an action...</option>
              <option value="repair">Send to Repair</option>
              <option value="wash">Send to Wash</option>
              <option value="complete">Mark as Complete</option>
            </select>
          </div>
          <div v-if="repairAction" class="mb-3">
            <label class="form-label">Notes</label>
            <textarea 
              v-model="repairNotes" 
              class="form-control" 
              rows="3" 
              placeholder="Add notes for the maintenance team..."
            ></textarea>
          </div>
          <div class="d-flex gap-2 justify-content-end mt-4">
            <button @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button 
              @click="submitRepair" 
              class="btn btn-primary"
              :disabled="!repairAction || isProcessing"
            >
              <span v-if="!isProcessing">Process</span>
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
const repairAction = ref('')
const repairNotes = ref('')

const filteredOrders = computed(() => {
  return orders.value.filter(order => {
    const query = searchQuery.value.toLowerCase()
    return (
      order.orderID.toLowerCase().includes(query) ||
      order.CustomerName.toLowerCase().includes(query) ||
      order.CustomerEmail.toLowerCase().includes(query)
    )
  })
})

const formatDate = (dateString) => {
  try {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
    return formatter.format(new Date(dateString))
  } catch {
    return dateString
  }
}

const getDamageClass = (status) => {
  switch (status) {
    case 1:
      return 'bg-warning'
    case 2:
      return 'bg-danger'
    case 3:
      return 'bg-info'
    default:
      return 'bg-secondary'
  }
}

const getDamageLabel = (status) => {
  switch (status) {
    case 1:
      return 'Light Damage'
    case 2:
      return 'Heavy Damage'
    case 3:
      return 'Urgent'
    default:
      return 'Unknown'
  }
}

const loadReturnsQueue = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'

    const [damagedOrders, pendingInspectionOrders] = await Promise.allSettled([
      fetchOrdersByStatus(orderApiUrl, 'RETURNED_DAMAGED'),
      fetchOrdersByStatus(orderApiUrl, 'RETURNED_PENDING_INSPECTION'),
    ])

    const damaged = damagedOrders.status === 'fulfilled' ? damagedOrders.value : []
    const pendingInspection = pendingInspectionOrders.status === 'fulfilled' ? pendingInspectionOrders.value : []

    orders.value = [...damaged, ...pendingInspection]
  } catch (error) {
    console.error('Error loading returns queue:', error)
  } finally {
    isLoading.value = false
  }
}

const refreshOrders = () => {
  loadReturnsQueue()
}

const processRepair = (orderId) => {
  selectedOrderId.value = orderId
  repairAction.value = ''
  repairNotes.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedOrderId.value = null
  repairAction.value = ''
  repairNotes.value = ''
}

const submitRepair = async () => {
  isProcessing.value = true
  processingId.value = selectedOrderId.value
  try {
    await AdminService.processReturnRepair(selectedOrderId.value, repairAction.value, repairNotes.value)
    orders.value = orders.value.filter(order => order.orderID !== selectedOrderId.value)
    closeModal()
  } catch (error) {
    console.error('Error processing return:', error)
    alert('Failed to process return: ' + error.message)
  } finally {
    isProcessing.value = false
    processingId.value = null
  }
}

onMounted(() => {
  loadReturnsQueue()
})
</script>

<style scoped>
.returns-queue-container {
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

.table {
  margin: 0;
  border-collapse: collapse;
}

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

.table tbody tr:hover {
  background-color: #faf9f7;
}

.table tbody td {
  padding: 1rem;
  border-bottom: 1px solid #e0ddd3;
  vertical-align: middle;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.badge {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-block;
  margin: 0;
}

.customer-info p {
  font-size: 0.95rem;
}

.gown-name {
  color: #d8a61c;
  font-weight: 600;
}

.damage-note {
  color: #dc3545;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #d8a61c;
  border-color: #d8a61c;
  color: white;
  border-radius: 8px;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-primary:disabled {
  opacity: 0.6;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  max-width: 450px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-content h4 {
  color: #2b3035;
  font-weight: 700;
}

.form-label {
  font-weight: 600;
  color: #2b3035;
  margin-bottom: 0.5rem;
}

.form-select,
.form-control {
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  background-color: white;
}

.form-select:focus,
.form-control:focus {
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
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
  .table {
    font-size: 0.85rem;
  }

  .table td, .table th {
    padding: 0.75rem;
  }

  .customer-info small {
    display: none;
  }
}
</style>
