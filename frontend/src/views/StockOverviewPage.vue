<template>
  <div class="overview-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Stock Overview</h2>
        <p class="text-muted mb-0">Review live stock-state here.</p>
      </div>

      <div class="panel">
        <div v-if="errorMessage" class="alert alert-danger mb-0">{{ errorMessage }}</div>

        <div class="orders-toolbar top-toolbar">
          <div class="search-box order-search">
            <i class="bi bi-search"></i>
            <input
              v-model="stockSearchQuery"
              type="text"
              class="form-control"
              placeholder="Search by model ID or item name"
            />
          </div>
        </div>

        <div class="status-toolbar">
          <label class="toolbar-label">Item Type</label>
          <div class="filter-pills">
            <button
              v-for="filter in stockTypeFilters"
              :key="filter.value"
              @click="selectedStockType = filter.value"
              :class="['filter-pill', { active: selectedStockType === filter.value }]"
            >
              {{ filter.label }}
            </button>
          </div>
        </div>

        <div class="advanced-filters">
          <div class="filter-group">
            <label class="toolbar-label">Size</label>
            <select v-model="selectedStockSize" class="form-select filter-select">
              <option value="ALL">All Sizes</option>
              <option v-for="size in stockSizeOptions" :key="size" :value="size">
                {{ size }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="filteredStockRows.length === 0 && !errorMessage" class="empty-state">
          <i class="bi bi-box-seam"></i>
          <p>No live stock rows matched the current filters.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table align-middle stock-table mb-0">
            <thead>
              <tr>
                <th>Model ID</th>
                <th>Item Name</th>
                <th>Type</th>
                <th>Size</th>
                <th>Total</th>
                <th>Available</th>
                <th>Reserved</th>
                <th>Rented</th>
                <th>Damaged</th>
                <th>Repair</th>
                <th>Wash</th>
                <th>Backup</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredStockRows" :key="item.modelId">
                <td class="fw-semibold">{{ item.modelId }}</td>
                <td>{{ item.itemName }}</td>
                <td class="text-uppercase">{{ item.itemType }}</td>
                <td>{{ item.size || '-' }}</td>
                <td>{{ item.totalQty }}</td>
                <td>{{ item.availableQty }}</td>
                <td>{{ item.reservedQty }}</td>
                <td>{{ item.rentedQty }}</td>
                <td>{{ item.damagedQty }}</td>
                <td>{{ item.repairQty }}</td>
                <td>{{ item.washQty }}</td>
                <td>{{ item.backupQty }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import inventoryService from '../services/inventory'

const stockOverview = ref([])
const errorMessage = ref('')
const stockSearchQuery = ref('')
const selectedStockType = ref('ALL')
const selectedStockSize = ref('ALL')
const stockTypeFilters = [
  { value: 'ALL', label: 'All' },
  { value: 'hood', label: 'HOOD' },
  { value: 'gown', label: 'GOWN' },
  { value: 'hat', label: 'HAT' }
]

const stockSizeOptions = computed(() =>
  [...new Set(stockOverview.value
    .map(item => item.size)
    .filter(size => size && size !== '-'))].sort((a, b) => a.localeCompare(b))
)

const filteredStockRows = computed(() => {
  const query = stockSearchQuery.value.trim().toLowerCase()

  return stockOverview.value
    .filter(item => {
      if (selectedStockType.value === 'ALL') return true
      return item.itemType === selectedStockType.value
    })
    .filter(item => {
      if (selectedStockSize.value === 'ALL') return true
      return item.size === selectedStockSize.value
    })
    .filter(item => {
      if (!query) return true
      return (
        item.modelId?.toLowerCase().includes(query) ||
        item.itemName?.toLowerCase().includes(query)
      )
    })
})

const loadStockOverview = async () => {
  errorMessage.value = ''
  try {
    stockOverview.value = await inventoryService.getStockOverview(new Date())
  } catch (error) {
    // console.error('Error loading stock overview:', error)
    errorMessage.value = error.message || 'Unable to load stock overview right now.'
    stockOverview.value = []
  }
}

onMounted(loadStockOverview)
</script>

<style scoped>
.overview-page {
  min-height: 100vh;
  background: #fbf7ef;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.panel {
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

.status-toolbar {
  margin-top: 1.25rem;
  margin-bottom: 1rem;
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

.advanced-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
  align-items: end;
}

.filter-group {
  width: min(100%, 220px);
}

.filter-select {
  min-height: 42px;
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  color: #6c6459;
}

.filter-select:focus {
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
}

.stock-table thead th {
  color: #7c7467;
  font-size: 0.76rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-bottom-color: #e9e2d6;
  white-space: nowrap;
}

.stock-table tbody td {
  font-size: 0.9rem;
  white-space: nowrap;
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

@media (max-width: 768px) {
  .order-search {
    min-width: 100%;
  }

  .filter-group,
  .filter-group-wide {
    min-width: 100%;
  }
}

</style>
