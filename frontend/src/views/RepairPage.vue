<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Repair Team</h2>
        <p class="text-muted mb-0">Handle damaged returns and send repaired items onward to laundry.</p>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-4">
          <div class="stat-card">
            <p class="stat-label">Repair Queue</p>
            <p class="stat-value">{{ repairQueue.length }}</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card">
            <p class="stat-label">Awaiting Laundry</p>
            <p class="stat-value">{{ washQueue.length }}</p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card">
            <p class="stat-label">Recently Completed</p>
            <p class="stat-value">{{ completedQueue.length }}</p>
          </div>
        </div>
      </div>

      <div class="team-card mb-4">
        <div class="section-head">
          <div>
            <h4 class="mb-1"><i class="bi bi-tools me-2"></i>Repair Queue</h4>
            <p class="text-muted mb-0">Items that need repair before they can move to wash.</p>
          </div>
          <button @click="loadData" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-clockwise"></i> Refresh
          </button>
        </div>

        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-3 text-muted">Loading repair queue...</p>
        </div>

        <div v-else-if="repairQueue.length === 0" class="empty-state">
          <i class="bi bi-check2-circle"></i>
          <p>No damaged items are waiting for repair.</p>
        </div>

        <div v-else class="queue-list">
          <div v-for="item in repairQueue" :key="item.id" class="queue-item">
            <div>
              <p class="item-title">{{ item.gownName }}</p>
              <p class="item-meta">Order {{ item.itemId }}</p>
              <p class="item-note">Issue: {{ item.issue }}</p>
              <p class="item-date">Returned: {{ formatDate(item.dateAdded) }}</p>
            </div>
            <button
              @click="markRepairComplete(item.itemId)"
              class="btn btn-success"
              :disabled="processingId === item.itemId"
            >
              <span v-if="processingId !== item.itemId">Send To Laundry</span>
              <span v-else>
                <span class="spinner-border spinner-border-sm me-1"></span>
                Updating...
              </span>
            </button>
          </div>
        </div>
      </div>

      <div class="team-card">
        <div class="section-head">
          <div>
            <h4 class="mb-1"><i class="bi bi-droplet me-2"></i>Sent To Laundry</h4>
            <p class="text-muted mb-0">Reference list of repaired orders that are now with the laundry team.</p>
          </div>
        </div>

        <div v-if="!isLoading && washQueue.length === 0" class="empty-state compact">
          <p>No repaired items have been handed off yet.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Order</th>
                <th>Item</th>
                <th>Issue</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in washQueue" :key="item.id">
                <td>{{ item.itemId }}</td>
                <td>{{ item.gownName }}</td>
                <td>{{ item.issue }}</td>
                <td><span class="badge bg-info">With Laundry</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { loadMaintenanceBuckets, readStageMap, writeStageMap } from '../services/admin/maintenance'

const repairQueue = ref([])
const washQueue = ref([])
const completedQueue = ref([])
const isLoading = ref(false)
const processingId = ref(null)

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

const loadData = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    const buckets = await loadMaintenanceBuckets(orderApiUrl)
    repairQueue.value = buckets.repairQueue
    washQueue.value = buckets.washQueue
    completedQueue.value = buckets.completedQueue
  } catch (error) {
    console.error('Error loading repair queue:', error)
  } finally {
    isLoading.value = false
  }
}

const markRepairComplete = async (itemId) => {
  processingId.value = itemId
  try {
    await AdminService.completeRepair(itemId)
    const stageMap = readStageMap()
    stageMap[itemId] = 'wash'
    writeStageMap(stageMap)
    await loadData()
  } catch (error) {
    console.error('Error completing repair:', error)
    alert('Failed to send item to laundry: ' + error.message)
  } finally {
    processingId.value = null
  }
}

onMounted(loadData)
</script>

<style scoped>
.team-page {
  min-height: 100vh;
  background: #fbf7ef;
  padding-top: 100px;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.team-card,
.stat-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.team-card {
  padding: 1.5rem;
}

.stat-card {
  padding: 1.25rem 1.5rem;
}

.stat-label {
  margin-bottom: 0.35rem;
  color: #7c7467;
  text-transform: uppercase;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
}

.stat-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #8a5f10;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.25rem;
}

.queue-list {
  display: grid;
  gap: 1rem;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.1rem;
  border-radius: 16px;
  background: #fcfaf5;
  border: 1px solid #e9dfc9;
}

.item-title {
  margin: 0 0 0.25rem;
  font-weight: 700;
  color: #2b3035;
}

.item-meta,
.item-note,
.item-date {
  margin: 0.2rem 0;
  color: #6c6459;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #7c7467;
}

.empty-state i {
  font-size: 2.5rem;
}

.empty-state.compact {
  padding: 1rem 0 0;
}

.btn-outline-secondary {
  border-color: #d8a61c;
  color: #d8a61c;
}

.btn-outline-secondary:hover {
  background: #d8a61c;
  color: white;
  border-color: #d8a61c;
}

@media (max-width: 768px) {
  .queue-item,
  .section-head {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
