<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Laundry</h2>
        <p class="text-muted mb-0">Items undergoing washing (3-day cycle). Status updates automatically.</p>
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
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in washQueue" :key="item.modelId">
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
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="info-banner mt-4">
        <i class="bi bi-info-circle me-2"></i>
        <div>
          <strong>Automatic Processing:</strong> Items in washing automatically transition to available inventory after 3 days.
          <br/>
          <strong>Backup Coverage:</strong> Backup stock allocated during washing period to maintain rental availability.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { loadMaintenanceBuckets } from '../services/admin/maintenance'

const washQueue = ref([])
const isLoading = ref(false)

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

// Auto-refresh every 30 seconds to show progress
onMounted(() => {
  loadData()
  const interval = setInterval(loadData, 30000)
  return () => clearInterval(interval)
})
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
  margin-bottom: 2rem;
}

.team-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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

.queue-table {
  overflow-x: auto;
}

.table {
  margin-bottom: 0;
}

.table thead th {
  background-color: #fbf7ef;
  color: #7c7467;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.76rem;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #e9e2d6;
  padding: 1rem;
}

.table tbody td {
  padding: 1rem;
  border-bottom: 1px solid #e9e2d6;
}

.progress {
  background-color: #e9e2d6;
}

.info-banner {
  background-color: #fef9f0;
  border: 1px solid #f0e8d8;
  border-radius: 12px;
  padding: 1rem;
  color: #6c6459;
  font-size: 0.9rem;
  line-height: 1.5;
}

.info-banner i {
  color: #d8a61c;
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
