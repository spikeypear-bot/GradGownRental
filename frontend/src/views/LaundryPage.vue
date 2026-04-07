<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Laundry</h2>
        <p class="text-muted mb-0">Items undergoing washing. Mark them complete when they are ready to return to available inventory.</p>
      </div>

      <div class="team-card">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-3 text-muted">Loading items in washing...</p>
        </div>

        <div v-else-if="washQueue.length === 0" class="empty-state">
          <i class="bi bi-droplet-half"></i>
          <p>No items currently in washing.</p>
        </div>

        <div v-else class="queue-table">
          <div class="table-responsive">
            <table class="table align-middle">
              <thead>
                <tr>
                  <th>Model ID</th>
                  <th>Item Name</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in washQueue" :key="item.queueKey">
                  <td class="fw-semibold">{{ item.modelId }}</td>
                  <td>{{ item.itemName }}</td>
                  <td class="text-uppercase text-muted">{{ item.itemType }}</td>
                  <td>{{ item.size }}</td>
                  <td><span class="badge bg-info">IN WASHING</span></td>
                  <td>
                    <div class="progress" style="height: 20px;">
                      <div class="progress-bar bg-info" role="progressbar" style="width: 33%" aria-valuenow="33" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                  </td>
                  <td>
                    <button
                      @click="markWashComplete(item)"
                      class="btn btn-sm btn-laundry"
                      :disabled="processingId === item.queueKey"
                    >
                      <span v-if="processingId !== item.queueKey">Mark Laundry Done</span>
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

      <div class="info-banner mt-4">
        <i class="bi bi-info-circle me-2"></i>
        <div>
          <strong>Laundry Flow:</strong> Washing completion is confirmed manually from this page before items return to available inventory.
          <br/>
          <strong>Backup Coverage:</strong> Backup stock supports availability during maintenance windows when staff activates it.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { loadMaintenanceBuckets, readMaintenanceDetails, writeMaintenanceDetails } from '../services/admin/maintenance'

const washQueue = ref([])
const isLoading = ref(false)
const processingId = ref(null)

const loadData = async () => {
  isLoading.value = true
  try {
    const orderApiUrl =
      import.meta.env.VITE_ORDER_API_BASE_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'
    const buckets = await loadMaintenanceBuckets(orderApiUrl)
    washQueue.value = buckets.washQueue
  } catch (error) {
    // console.error('Error loading laundry queue:', error)
  } finally {
    isLoading.value = false
  }
}

const markWashComplete = async (item) => {
  processingId.value = item.queueKey
  try {
    const detailsMap = readMaintenanceDetails()
    const entry = { ...(detailsMap[item.orderId] || {}) }

    if (item.subsetKey === 'clean') {
      entry.cleanItemStages = {
        ...(entry.cleanItemStages || {}),
        [item.queueKey]: 'done'
      }
    } else if (item.subsetKey === 'damaged') {
      entry.damagedItemStages = {
        ...(entry.damagedItemStages || {}),
        [item.queueKey]: 'done'
      }
    }

    const remainingStages = [
      ...Object.values(entry.cleanItemStages || {}),
      ...Object.values(entry.damagedItemStages || {})
    ].filter(stage => stage && stage !== 'done')
    const completeOrder = remainingStages.length === 0

    await AdminService.completeWash(item.orderId, item?.selectedPackages || null, { completeOrder })
    detailsMap[item.orderId] = entry
    writeMaintenanceDetails(detailsMap)
    await loadData()
  } catch (error) {
    // console.error('Error completing wash:', error)
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

