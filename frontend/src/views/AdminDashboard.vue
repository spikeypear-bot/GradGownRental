<template>
  <div class="admin-dashboard">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">View Orders</h2>
        <p class="text-muted mb-0">Review operational orders here.</p>
      </div>

      <div class="orders-panel">
        <div class="orders-toolbar top-toolbar">
          <div class="search-box order-search">
            <i class="bi bi-search"></i>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search by order ID"
            />
          </div>
        </div>

        <div class="status-toolbar">
          <label class="toolbar-label">Order Status</label>
          <div class="filter-pills">
            <button
              v-for="status in orderStatuses"
              :key="status.value"
              @click="selectedStatus = status.value"
              :class="['filter-pill', { active: selectedStatus === status.value }]"
            >
              {{ status.label }}
            </button>
          </div>
        </div>

        <div v-if="errorMessage" class="alert alert-danger mt-3 mb-0">{{ errorMessage }}</div>

        <div v-if="isLoading" class="empty-state">
          <div class="spinner-border" role="status"></div>
          <p>Loading orders...</p>
        </div>

        <div v-else-if="filteredOrders.length === 0" class="empty-state">
          <i class="bi bi-inbox"></i>
          <p>{{ emptyStateMessage }}</p>
        </div>

        <div v-else class="table-responsive mt-3">
          <table class="table align-middle orders-table mb-0">
            <thead>
              <tr>
                <th>Order</th>
                <th>Student</th>
                <th>Email Status</th>
                <th>Fulfillment</th>
                <th>Rental Date</th>
                <th>Return Date</th>
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.orderID">
                <td class="fw-semibold">{{ order.orderID }}</td>
                <td>
                  <span class="student-cell">
                    <span class="fw-semibold text-dark">{{ order.CustomerName || 'Student' }}</span>
                    <span class="student-divider">|</span>
                    <span class="text-muted">{{ order.CustomerEmail || '-' }}</span>
                  </span>
                </td>
                <td>
                  <span :class="['status-chip', getEmailStatusClass(emailStatusMap[order.orderID])]">
                    {{ emailStatusMap[order.orderID] || 'UNKNOWN' }}
                  </span>
                </td>
                <td>{{ order.fulfillment_method || '-' }}</td>
                <td>{{ formatDate(order.rental_start_date) }}</td>
                <td>{{ formatDate(order.rental_end_date) }}</td>
                <td>SGD ${{ Number(order.TotalAmount || 0).toFixed(2) }}</td>
                <td>
                  <span :class="['status-chip', statusClass(order.status)]">
                    {{ order.status || '-' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { fetchOrdersByStatus, fetchEmailStatusForOrder } from '../services/admin/helpers'

const orderApiUrl =
  import.meta.env.VITE_ORDER_API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000'
const backendStatuses = ['CONFIRMED', 'ACTIVE', 'RETURNED_DAMAGED', 'COMPLETED']
const orderStatuses = [
  { value: 'ALL', label: 'All' },
  ...backendStatuses.map(status => ({
    value: status,
    label: status
  }))
]

const orders = ref([])
const emailStatusMap = ref({})
const selectedStatus = ref('ALL')
const searchQuery = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const filteredOrders = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return orders.value

  return orders.value.filter(order => order.orderID?.toLowerCase().includes(query))
})

const emptyStateMessage = computed(() => {
  if (selectedStatus.value === 'ALL') {
    return 'No orders matched the current search or filter.'
  }

  return `No ${selectedStatus.value.toLowerCase()} orders matched the current search or filter.`
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(dateString))
  } catch {
    return dateString
  }
}

const statusClass = (status) => {
  switch (status) {
    case 'COMPLETED':
      return 'status-completed'
    case 'RETURNED_DAMAGED':
      return 'status-damaged'
    case 'CONFIRMED':
      return 'status-confirmed'
    case 'ACTIVE':
    default:
      return 'status-active'
  }
}

const getEmailStatusClass = (status) => {
  const normalized = (status || '').toUpperCase()
  if (normalized.startsWith('CONFIRMATION') || normalized.startsWith('COLLECTION') || normalized.startsWith('RETURN') || normalized.startsWith('DEPOSIT')) {
    return normalized.includes('(FAILED)') ? 'status-damaged' : 'status-completed'
  }

  switch (normalized) {
    case 'SENT':
      return 'status-completed'
    case 'FAILED':
      return 'status-damaged'
    case 'PENDING':
      return 'status-confirmed'
    case 'NOT SENT':
    default:
      return 'status-active'
  }
}

const loadOrders = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    if (selectedStatus.value === 'ALL') {
      const results = await Promise.allSettled(
        backendStatuses.map(status => fetchOrdersByStatus(orderApiUrl, status))
      )

      const loadedOrders = []
      const seenOrderIds = new Set()

      for (const result of results) {
        if (result.status !== 'fulfilled') continue

        for (const order of result.value) {
          if (!order?.orderID || seenOrderIds.has(order.orderID)) continue
          seenOrderIds.add(order.orderID)
          loadedOrders.push(order)
        }
      }

      orders.value = loadedOrders
    } else {
      orders.value = await fetchOrdersByStatus(orderApiUrl, selectedStatus.value)
    }

    const statusPairs = await Promise.all(
      orders.value.map(async (order) => {
        const orderId = order?.orderID
        const status = await fetchEmailStatusForOrder(orderId)
        return [orderId, status]
      })
    )

    emailStatusMap.value = Object.fromEntries(statusPairs.filter(([orderId]) => !!orderId))
  } catch (error) {
    console.error('Error loading orders:', error)
    errorMessage.value = error.message || 'Unable to load orders right now.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadOrders()
})

watch(selectedStatus, () => {
  loadOrders()
})
</script>

<style scoped>
.admin-dashboard {
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

.orders-panel {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.orders-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: stretch;
}

.top-toolbar {
  justify-content: space-between;
}

.search-box {
  position: relative;
}

.status-toolbar {
  margin-top: 1.25rem;
}

.toolbar-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #7c7467;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.filter-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-pill {
  border: 1px solid #e0ddd3;
  background: white;
  color: #6c6459;
  border-radius: 999px;
  padding: 0.55rem 0.9rem;
  font-weight: 600;
}

.filter-pill.active {
  background: #fff0da;
  border-color: #d8a61c;
  color: #b38310;
}

.order-search {
  min-width: min(100%, 360px);
  flex: 1;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #d8a61c;
}

.search-box .form-control {
  height: 100%;
  min-height: 42px;
  padding-left: 2.5rem;
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  background-color: white;
}

.search-box .form-control:focus {
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #7c7467;
}

.empty-state i {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.75rem;
  color: #d8a61c;
}

.empty-state p {
  margin: 0.75rem 0 0;
}

.orders-table thead th {
  color: #7c7467;
  font-size: 0.72rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-bottom-color: #e9e2d6;
  white-space: nowrap;
}

.orders-table tbody td {
  padding-top: 1rem;
  padding-bottom: 1rem;
  font-size: 0.9rem;
  white-space: nowrap;
  vertical-align: middle;
}

.student-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  white-space: nowrap;
}

.student-divider {
  color: #c2b8a7;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.status-active {
  background: #fff0da;
  color: #b38310;
}

.status-completed {
  background: #e8f6ec;
  color: #22804a;
}

.status-confirmed {
  background: #e9f2ff;
  color: #2757a5;
}

.status-damaged {
  background: #fdeaea;
  color: #b74141;
}


@media (max-width: 1024px) {
  .admin-dashboard {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .top-toolbar {
    align-items: stretch;
  }

  .order-search {
    min-width: 100%;
  }
}
</style>
