<template>
  <div class="maintenance-container">
    <div class="container py-4">
      <div class="mb-4">
        <h2 class="fw-bold mb-2">Maintenance Workflow</h2>
        <p class="text-muted">Manage gown repairs and washing operations</p>
        <p v-if="isDemoMode" class="text-warning mb-0 small">Demo mode is on. Maintenance queues use the same UI flow without waiting on calendar timing.</p>
      </div>

      <!-- Maintenance Sections -->
      <div class="row g-4 mb-5">
        <!-- Repair Queue -->
        <div class="col-lg-6">
          <div class="maintenance-card">
            <div class="card-header">
              <h4><i class="bi bi-tools"></i> Repair Queue</h4>
              <span class="badge bg-danger">{{ repairQueue.length }}</span>
            </div>
            <div class="card-body">
              <div v-if="loadingRepair" class="text-center py-3">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="repairQueue.length === 0" class="text-center py-5 text-muted">
                <i class="bi bi-check-circle" style="font-size: 2.5rem;"></i>
                <p class="mt-2">No items in repair queue</p>
              </div>
              <div v-else class="queue-items">
                <div v-for="item in repairQueue" :key="item.id" class="queue-item">
                  <div class="item-header">
                    <strong>{{ item.gownName }}</strong>
                    <span class="tiny-badge">{{ item.itemId }}</span>
                  </div>
                  <p class="item-issue">Issue: {{ item.issue }}</p>
                  <p class="item-date">Added: {{ formatDate(item.dateAdded) }}</p>
                  <button 
                    @click="markRepairComplete(item)"
                    class="btn btn-sm btn-success"
                    :disabled="processingId === item.id"
                  >
                      <span v-if="processingId !== item.id">
                      <i class="bi bi-check"></i> Mark Complete
                    </span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Submitting...
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Wash Queue -->
        <div class="col-lg-6">
          <div class="maintenance-card">
            <div class="card-header">
              <h4><i class="bi bi-droplet"></i> Wash Queue</h4>
              <span class="badge bg-info">{{ washQueue.length }}</span>
            </div>
            <div class="card-body">
              <div v-if="loadingWash" class="text-center py-3">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="washQueue.length === 0" class="text-center py-5 text-muted">
                <i class="bi bi-check-circle" style="font-size: 2.5rem;"></i>
                <p class="mt-2">No items in wash queue</p>
              </div>
              <div v-else class="queue-items">
                <div v-for="item in washQueue" :key="item.id" class="queue-item">
                  <div class="item-header">
                    <strong>{{ item.gownName }}</strong>
                    <span class="tiny-badge">{{ item.itemId }}</span>
                  </div>
                  <p class="item-condition">Condition: {{ item.condition }}</p>
                  <p class="item-date">Added: {{ formatDate(item.dateAdded) }}</p>
                  <button 
                    @click="markWashComplete(item)"
                    class="btn btn-sm btn-primary"
                    :disabled="processingId === item.id"
                  >
                      <span v-if="processingId !== item.id">
                      <i class="bi bi-check"></i> Mark Complete
                    </span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-1"></span>
                      Submitting...
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Ready for Return -->
      <div class="row g-4">
        <div class="col-12">
          <div class="maintenance-card">
            <div class="card-header">
              <h4><i class="bi bi-checkmark-square"></i> Ready for Return</h4>
              <span class="badge bg-success">{{ readyForReturn.length }}</span>
            </div>
            <div class="card-body">
              <div v-if="loadingReady" class="text-center py-3">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="readyForReturn.length === 0" class="text-center py-5 text-muted">
                <i class="bi bi-inbox-empty" style="font-size: 2.5rem;"></i>
                <p class="mt-2">No items ready for return</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Gown</th>
                      <th>Item ID</th>
                      <th>Maintenance History</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in readyForReturn" :key="item.id">
                      <td><strong>{{ item.gownName }}</strong></td>
                      <td><span class="tiny-badge">{{ item.itemId }}</span></td>
                      <td>
                        <small class="text-muted">
                          Repaired at {{ formatDate(item.repairDate) }}<br>
                          Washed at {{ formatDate(item.washDate) }}
                        </small>
                      </td>
                      <td>
                        <button 
                          @click="markReadyToReturn(item)"
                          class="btn btn-sm btn-outline-success"
                          :disabled="processingId === item.id"
                        >
                          <span v-if="processingId !== item.id">Return</span>
                          <span v-else>
                            <span class="spinner-border spinner-border-sm me-1"></span>
                            Updating...
                          </span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Maintenance Stats -->
      <div class="row g-3 mt-4">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon repair">
              <i class="bi bi-tools"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Repairs in Progress</p>
              <p class="stat-value">{{ repairQueue.length }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon wash">
              <i class="bi bi-droplet"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Washes in Progress</p>
              <p class="stat-value">{{ washQueue.length }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon ready">
              <i class="bi bi-check-circle"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Ready to Return</p>
              <p class="stat-value">{{ readyForReturn.length }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon total">
              <i class="bi bi-stack"></i>
            </div>
            <div class="stat-content">
              <p class="stat-label">Total Items</p>
              <p class="stat-value">{{ repairQueue.length + washQueue.length + readyForReturn.length }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminService from '../services/admin'
import { isDemoMode } from '../config/demoMode'
import { loadMaintenanceBuckets, readMaintenanceDetails, writeMaintenanceDetails } from '../services/admin/maintenance'

const repairQueue = ref([])
const washQueue = ref([])
const readyForReturn = ref([])

const loadingRepair = ref(false)
const loadingWash = ref(false)
const loadingReady = ref(false)
const processingId = ref(null)

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

const loadMaintenanceData = async () => {
  loadingRepair.value = true
  loadingWash.value = true
  loadingReady.value = true

  try {
    const orderApiUrl =
      import.meta.env.VITE_ORDER_API_BASE_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'
    const buckets = await loadMaintenanceBuckets(orderApiUrl)
    repairQueue.value = buckets.repairQueue
    washQueue.value = buckets.washQueue
    readyForReturn.value = buckets.completedQueue
  } catch (error) {
    console.error('Error loading maintenance data:', error)
  } finally {
    loadingRepair.value = false
    loadingWash.value = false
    loadingReady.value = false
  }
}

const markRepairComplete = async (item) => {
  processingId.value = item.id
  try {
    await AdminService.completeRepair(item.itemId, item?.selectedPackages || null)
    const detailsMap = readMaintenanceDetails()
    const entry = { ...(detailsMap[item.itemId] || {}) }
    if (item.subsetKey === 'damaged') {
      entry.damagedStage = 'wash'
    }
    detailsMap[item.itemId] = entry
    writeMaintenanceDetails(detailsMap)
    await loadMaintenanceData()
  } catch (error) {
    console.error('Error completing repair:', error)
    alert('Failed to complete repair: ' + error.message)
  } finally {
    processingId.value = null
  }
}

const markWashComplete = async (item) => {
  processingId.value = item.id
  try {
    const detailsMap = readMaintenanceDetails()
    const entry = { ...(detailsMap[item.itemId] || {}) }

    if (item.subsetKey === 'clean') {
      entry.cleanStage = 'done'
    } else if (item.subsetKey === 'damaged') {
      entry.damagedStage = 'done'
    }

    const remainingStages = [entry.cleanStage, entry.damagedStage].filter(stage => stage && stage !== 'done')
    const completeOrder = remainingStages.length === 0

    await AdminService.completeWash(item.itemId, item?.selectedPackages || null, { completeOrder })
    detailsMap[item.itemId] = entry
    writeMaintenanceDetails(detailsMap)
    await loadMaintenanceData()
  } catch (error) {
    console.error('Error completing wash:', error)
    alert('Failed to complete wash: ' + error.message)
  } finally {
    processingId.value = null
  }
}

const markReadyToReturn = async (item) => {
  processingId.value = item.id
  try {
    await AdminService.markItemComplete(item.itemId, item?.selectedPackages || null, { completeOrder: true })
    readyForReturn.value = readyForReturn.value.filter(entry => entry.id !== item.id)
  } catch (error) {
    console.error('Error marking item complete:', error)
    alert('Failed to mark item complete: ' + error.message)
  } finally {
    processingId.value = null
  }
}

onMounted(() => {
  loadMaintenanceData()
})
</script>

<style scoped>
.maintenance-container {
  min-height: 100vh;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
}

.maintenance-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  background-color: #f9f7f2;
  padding: 1.5rem;
  border-bottom: 1px solid #e0ddd3;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: #2b3035;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.card-header .badge {
  min-width: 40px;
  text-align: center;
}

.card-body {
  padding: 1.5rem;
}

.queue-items {
  display: grid;
  gap: 1rem;
}

.queue-item {
  padding: 1rem;
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  background-color: #fafaf9;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.tiny-badge {
  background-color: #d8a61c;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.item-issue,
.item-condition,
.item-date {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.queue-item .btn {
  margin-top: 0.75rem;
  width: 100%;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
  border-radius: 8px;
  font-weight: 600;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
  border-color: #218838;
}

.btn-primary {
  background-color: #d8a61c;
  border-color: #d8a61c;
  border-radius: 8px;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-outline-success {
  border-color: #28a745;
  color: #28a745;
  border-radius: 8px;
  font-weight: 600;
}

.btn-outline-success:hover:not(:disabled) {
  background-color: #28a745;
  border-color: #28a745;
  color: white;
}

.table {
  font-size: 0.9rem;
}

.table thead th {
  background-color: #f9f7f2;
  border-top: none;
  font-weight: 700;
  color: #2b3035;
  border-bottom: 1px solid #e0ddd3;
}

.table tbody td {
  border-color: #e0ddd3;
  vertical-align: middle;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.repair {
  background-color: #ffc107;
}

.stat-icon.wash {
  background-color: #17a2b8;
}

.stat-icon.ready {
  background-color: #28a745;
}

.stat-icon.total {
  background-color: #d8a61c;
}

.stat-content p {
  margin: 0;
}

.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2b3035;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .table {
    font-size: 0.8rem;
  }

  .table td, .table th {
    padding: 0.5rem;
  }

  .stat-card {
    justify-content: center;
    text-align: center;
  }
}
</style>
