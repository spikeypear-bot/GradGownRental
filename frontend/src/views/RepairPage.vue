<template>
  <div class="team-page">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Repair</h2>
        <p class="text-muted mb-0">Items undergoing repair. Move them to washing only after staff confirms the repair is done.</p>
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
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in repairQueue" :key="item.queueKey">
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
                  <td>
                    <button
                      @click="markRepairComplete(item)"
                      class="btn btn-sm btn-repair"
                      :disabled="processingId === item.queueKey"
                    >
                      <span v-if="processingId !== item.queueKey">Mark As Repaired</span>
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
          <strong>Repair Flow:</strong> Repair is a manual step. Items stay here until staff marks them as repaired, then they move to washing.
          <br/>
          <strong>Backup Coverage:</strong> Backup stock can be used while damaged items are under maintenance, but it is not auto-assigned from this screen.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { loadMaintenanceBuckets, readMaintenanceDetails, writeMaintenanceDetails } from '../services/admin/maintenance'

const repairQueue = ref([])
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
    repairQueue.value = buckets.repairQueue
  } catch (error) {
    // console.error('Error loading repair queue:', error)
  } finally {
    isLoading.value = false
  }
}

const markRepairComplete = async (item) => {
  processingId.value = item.queueKey
  try {
    await AdminService.completeRepair(item.orderId, item?.selectedPackages || null)
    const detailsMap = readMaintenanceDetails()
    const entry = { ...(detailsMap[item.orderId] || {}) }
    if (item.subsetKey === 'damaged') {
      entry.damagedItemStages = {
        ...(entry.damagedItemStages || {}),
        [item.queueKey]: 'wash'
      }
    }
    detailsMap[item.orderId] = entry
    writeMaintenanceDetails(detailsMap)
    await loadData()
  } catch (error) {
    // console.error('Error completing repair:', error)
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


