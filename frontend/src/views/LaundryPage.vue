<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Laundry Team</h2>
        <p class="text-muted mb-0">Mark washed orders as done so stock can move back into circulation.</p>
      </div>

      <div class="team-card">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-3 text-muted">Loading laundry queue...</p>
        </div>

        <div v-else-if="washQueue.length === 0" class="empty-state">
          <i class="bi bi-droplet-half"></i>
          <p>No orders are currently in washing.</p>
        </div>

        <div v-else class="queue-list">
          <div v-for="item in washQueue" :key="item.id" class="queue-item">
            <div class="item-info">
              <span class="item-id">{{ item.itemId }}</span>
              <p class="item-title mb-0">{{ item.gownName }}</p>
            </div>
            <button
              @click="markWashComplete(item.itemId)"
              class="btn btn-sm btn-laundry"
              :disabled="processingId === item.itemId"
            >
              <span v-if="processingId !== item.itemId">Mark Laundry Done</span>
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
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { loadMaintenanceBuckets, readStageMap, writeStageMap } from '../services/admin/maintenance'

const washQueue = ref([])
const isLoading = ref(false)
const processingId = ref(null)

const loadData = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    const buckets = await loadMaintenanceBuckets(orderApiUrl)
    washQueue.value = buckets.washQueue
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
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.team-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.875rem 1rem;
  border-radius: 12px;
  background: #f9f7f2;
  transition: background-color 0.2s ease;
}

.queue-item:hover {
  background: #f3eedf;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-id {
  font-size: 0.82rem;
  font-weight: 700;
  color: #999;
  display: block;
  word-break: break-all;
}

.item-title {
  font-weight: 600;
  color: #2b3035;
  font-size: 0.95rem;
}

.btn-laundry {
  background-color: #2b6cb0;
  border-color: #2b6cb0;
  color: white;
  border-radius: 10px;
  font-weight: 700;
}

.btn-laundry:hover:not(:disabled) {
  background-color: #1f4f82;
  border-color: #1f4f82;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6d7b7a;
}

.empty-state i {
  font-size: 2.5rem;
}

@media (max-width: 768px) {
  .queue-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
