<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Repair</h2>
        <p class="text-muted mb-0">Items undergoing repair (1-day maintenance window). Status updates automatically.</p>
      </div>

      <div class="team-card">
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-3 text-muted">Loading items in repair...</p>
        </div>

        <div v-else-if="repairQueue.length === 0" class="empty-state">
          <i class="bi bi-tools"></i>
          <p>No items currently in repair.</p>
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
                <tr v-for="item in repairQueue" :key="item.modelId">
                  <td class="fw-semibold">{{ item.modelId }}</td>
                  <td>{{ item.itemName }}</td>
                  <td class="text-uppercase text-muted">{{ item.itemType }}</td>
                  <td>{{ item.size }}</td>
                  <td><span class="badge bg-warning">IN REPAIR</span></td>
                  <td>
                    <div class="progress" style="height: 20px;">
                      <div class="progress-bar bg-warning" role="progressbar" style="width: 50%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
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
          <strong>Automatic Processing:</strong> Items automatically transition through repair (1 day) → washing (3 days) → available inventory.
          <br/>
          <strong>Backup Coverage:</strong> Backup stock automatically allocated while items are in maintenance.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { loadMaintenanceBuckets } from '../services/admin/maintenance'

const repairQueue = ref([])
const isLoading = ref(false)

const loadData = async () => {
  isLoading.value = true
  try {
    const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    const buckets = await loadMaintenanceBuckets(orderApiUrl)
    repairQueue.value = buckets.repairQueue
  } catch (error) {
    console.error('Error loading repair queue:', error)
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

.btn-repair {
  background-color: #2f855a;
  border-color: #2f855a;
  color: white;
  border-radius: 10px;
  font-weight: 700;
}

.btn-repair:hover:not(:disabled) {
  background-color: #276749;
  border-color: #276749;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #7c7467;
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
