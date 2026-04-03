<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Laundry Team</h2>
        <p class="text-muted mb-0">Wash repaired items, then complete the return workflow back to inventory.</p>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="stat-card">
            <p class="stat-label">Laundry Queue</p>
            <p class="stat-value">{{ washQueue.length }}</p>
          </div>
        </div>
        <div class="col-md-6">
          <div class="stat-card">
            <p class="stat-label">Recently Completed</p>
            <p class="stat-value">{{ completedQueue.length }}</p>
          </div>
        </div>
      </div>

      <div class="team-card mb-4">
        <div class="section-head">
          <div>
            <h4 class="mb-1"><i class="bi bi-droplet-half me-2"></i>Laundry Queue</h4>
            <p class="text-muted mb-0">Items that have been repaired and are ready for washing.</p>
          </div>
          <button @click="loadData" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-clockwise"></i> Refresh
          </button>
        </div>

        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-3 text-muted">Loading laundry queue...</p>
        </div>

        <div v-else-if="washQueue.length === 0" class="empty-state">
          <i class="bi bi-check2-circle"></i>
          <p>No items are currently waiting for laundry.</p>
        </div>

        <div v-else class="queue-list">
          <div v-for="item in washQueue" :key="item.id" class="queue-item">
            <div>
              <p class="item-title">{{ item.gownName }}</p>
              <p class="item-meta">Order {{ item.itemId }}</p>
              <p class="item-note">Issue: {{ item.issue }}</p>
              <p class="item-date">Handed over: {{ formatDate(item.dateAdded) }}</p>
            </div>
            <button
              @click="markWashComplete(item.itemId)"
              class="btn btn-primary"
              :disabled="processingId === item.itemId"
            >
              <span v-if="processingId !== item.itemId">Mark Laundry Complete</span>
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
            <h4 class="mb-1"><i class="bi bi-check2-square me-2"></i>Recently Completed</h4>
            <p class="text-muted mb-0">Orders completed after washing and returned to available inventory.</p>
          </div>
        </div>

        <div v-if="!isLoading && completedQueue.length === 0" class="empty-state compact">
          <p>No completed laundry records yet.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Order</th>
                <th>Item</th>
                <th>Completed At</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in completedQueue" :key="item.id">
                <td>{{ item.itemId }}</td>
                <td>{{ item.gownName }}</td>
                <td>{{ formatDate(item.washDate) }}</td>
                <td><span class="badge bg-success">Completed</span></td>
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
    washQueue.value = buckets.washQueue
    completedQueue.value = buckets.completedQueue
  } catch (error) {
    console.error('Error loading laundry queue:', error)
  } finally {
    isLoading.value = false
  }
}

const markWashComplete = async (itemId) => {
  processingId.value = itemId
  try {
    await AdminService.completeWash(itemId)
    const stageMap = readStageMap()
    delete stageMap[itemId]
    writeStageMap(stageMap)
    await loadData()
  } catch (error) {
    console.error('Error completing wash:', error)
    alert('Failed to complete laundry: ' + error.message)
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
  color: #2b7a78;
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
  background: #f4fbfa;
  border: 1px solid #cfeae7;
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
  color: #5d6a69;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6d7b7a;
}

.empty-state i {
  font-size: 2.5rem;
}

.empty-state.compact {
  padding: 1rem 0 0;
}

.btn-outline-secondary {
  border-color: #2b7a78;
  color: #2b7a78;
}

.btn-outline-secondary:hover {
  background: #2b7a78;
  color: white;
  border-color: #2b7a78;
}

@media (max-width: 768px) {
  .queue-item,
  .section-head {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
