<template>
  <div class="returns-queue-container">
    <div class="container-fluid py-4">
      <div class="content-wrapper">
        <div class="mb-4">
          <h2 class="fw-bold mb-2">Check Damage</h2>
          <p class="text-muted">Orders returned by customers awaiting damage inspection</p>
          <p v-if="isDemoMode" class="text-warning mb-0 small">Demo mode is on. Returned items are immediately available for damage inspection.</p>
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
          <p class="mt-3 text-muted">Loading damage inspection queue...</p>
        </div>

        <!-- Orders Table -->
        <div v-else class="orders-card">
          <div v-if="filteredItems.length === 0" class="text-center py-5">
            <i class="bi bi-inbox" style="font-size: 3rem; color: #d8a61c;"></i>
            <p class="mt-3 text-muted">No returned items pending damage inspection</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Model ID</th>
                <th>Type</th>
                <th>Size</th>
                <th>Returned Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredItems" :key="item.id">
                <td>
                  <span class="badge bg-light text-dark">{{ item.orderID }}</span>
                </td>
                <td>
                  <div class="customer-info">
                    <p class="mb-0 fw-500">{{ item.customerName }}</p>
                    <small class="text-muted">{{ item.customerEmail }}</small>
                  </div>
                </td>
                <td>
                  <span class="model-id">{{ item.modelId }}</span>
                </td>
                <td class="text-uppercase text-muted">{{ item.itemType }}</td>
                <td>{{ item.size }}</td>
                <td>{{ formatDate(item.returnedDate) }}</td>
                <td>
                  <button 
                    @click="processRepair(item.orderID, item)"
                    class="btn btn-sm btn-primary"
                    :disabled="processingId === item.orderID"
                  >
                    <span v-if="processingId !== item.orderID">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminService from '../services/admin'
import { isDemoMode } from '../config/demoMode'

const orders = ref([])
const items = ref([])
const searchQuery = ref('')
const isLoading = ref(false)
const showModal = ref(false)
const selectedOrderId = ref(null)
const selectedItem = ref(null)
const processingId = ref(null)
const isProcessing = ref(false)
const repairAction = ref('')
const repairNotes = ref('')

const filteredItems = computed(() => {
  return items.value.filter(item => {
    const query = searchQuery.value.toLowerCase()
    return (
      item.orderID.toLowerCase().includes(query) ||
      item.customerName.toLowerCase().includes(query) ||
      item.customerEmail.toLowerCase().includes(query) ||
      item.modelId.toLowerCase().includes(query)
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

// Fetch item details from inventory service (fallback if not in order)
async function fetchItemDetails(modelId) {
  try {
    const inventoryUrl = import.meta.env.VITE_INVENTORY_API_BASE_URL || 'http://localhost:8080'
    const response = await fetch(`${inventoryUrl}/api/inventory/models/${modelId}`)
    if (response.ok) {
      const result = await response.json()
      if (result && result.data) {
        // Successfully fetched from inventory
        return {
          modelId: result.data.modelId || modelId,
          itemName: result.data.style?.itemName || 'Unknown Item',
          itemType: result.data.style?.itemType || 'Gown',
          size: result.data.size || 'Unknown Size',
          totalQty: result.data.totalQty
        }
      }
    }
  } catch (error) {
    console.warn(`Failed to fetch item details for ${modelId}:`, error)
  }
  // Fallback for missing data
  return {
    modelId,
    itemName: 'Unknown Item',
    itemType: 'Gown',
    size: 'Unknown Size'
  }
}

const loadReturnsQueue = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    // Fetch RETURNED orders (items that have been marked as returned, awaiting damage inspection)
    const response = await fetch(`${orderApiUrl}/orders/status/RETURNED`)
    if (response.ok) {
      let data = await response.json()
      
      // Convert orders to items (one row per item)
      const expandedItems = []
      for (const order of data) {
        const orderID = order.order_id || order.orderID
        const customerName = order.student_name || order.CustomerName
        const customerEmail = order.email || order.CustomerEmail
        const returnedDate = order.returned_at || new Date().toISOString()
        const selectedItems = order.selected_items || []

        // Fetch details for all items in this order
        for (const item of selectedItems) {
          // Use size from order if available, otherwise fetch from inventory
          let size = item.size || ''
          let itemName = item.itemName || ''
          let itemType = item.itemType || ''
          
          // If size not in order, fetch from inventory
          if (!size) {
            const details = await fetchItemDetails(item.modelId)
            size = details.size
            itemName = details.itemName
            itemType = details.itemType
          }
          
          expandedItems.push({
            id: `${orderID}-${item.modelId}`, // Unique key for the row
            orderID,
            customerName,
            customerEmail,
            modelId: item.modelId,
            itemName: itemName,
            itemType: itemType,
            size: size,
            qty: item.qty || 1,
            returnedDate
          })
        }
      }
      items.value = expandedItems
    }
  } catch (error) {
    console.error('Error loading damage inspection queue:', error)
  } finally {
    isLoading.value = false
  }
}

const refreshOrders = () => {
  loadReturnsQueue()
}

const processRepair = (orderId, item) => {
  selectedOrderId.value = orderId
  selectedItem.value = item
  repairAction.value = ''
  repairNotes.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedOrderId.value = null
  selectedItem.value = null
  repairAction.value = ''
  repairNotes.value = ''
}

const submitRepair = async () => {
  isProcessing.value = true
  processingId.value = selectedOrderId.value
  try {
    await AdminService.processReturnRepair(selectedOrderId.value, repairAction.value, repairNotes.value)
    // Remove the processed item from the list
    items.value = items.value.filter(item => item.id !== selectedItem.value.id)
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

.content-wrapper {
  padding: 0 1rem;
  max-width: 1400px;
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

.orders-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.table-responsive {
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

.model-id {
  color: #d8a61c;
  font-weight: 600;
  font-family: 'Courier New', monospace;
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
