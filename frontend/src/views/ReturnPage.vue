<template>
  <div class="return-container">
    <div class="container py-4">
      <div class="row g-4">
        <!-- Return Processing Form -->
        <div class="col-lg-6">
          <div class="form-card">
            <h2>Process Return</h2>
            <p class="text-muted">Record gown returns and damage assessment</p>

            <form @submit.prevent="submitReturn">
              <div class="mb-3">
                <label for="orderId" class="form-label">Order ID</label>
                <input
                  id="orderId"
                  v-model="orderId"
                  type="text"
                  class="form-control"
                  placeholder="Enter order ID"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="damageReport" class="form-label">Damage Report</label>
                <textarea
                  id="damageReport"
                  v-model="damageReport"
                  class="form-control"
                  rows="4"
                  placeholder="Describe any damage to the gown..."
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="damageFee" class="form-label">Damage Fee ($)</label>
                <input
                  id="damageFee"
                  v-model.number="damageFee"
                  type="number"
                  class="form-control"
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                  required
                />
              </div>

              <button type="submit" class="btn btn-primary w-100">
                <span v-if="!isLoading">Process Return</span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Processing...
                </span>
              </button>
            </form>

            <div v-if="successMessage" class="alert alert-success mt-3" role="alert">
              {{ successMessage }}
            </div>
            <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
              {{ errorMessage }}
            </div>
          </div>
        </div>

        <!-- Maintenance Workflow -->
        <div class="col-lg-6">
          <div class="workflow-card">
            <h2>Maintenance Workflow</h2>
            <p class="text-muted">Manage gown maintenance status</p>

            <div class="workflow-section mb-3">
              <h5>Transition to Wash</h5>
              <form @submit.prevent="submitTransitionToWash">
                <div class="mb-3">
                  <input
                    v-model="washOrderId"
                    type="text"
                    class="form-control"
                    placeholder="Enter order ID to send for wash"
                    required
                  />
                </div>
                <button type="submit" class="btn btn-secondary w-100">
                  <span v-if="!isLoadingWash">Send to Wash</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Processing...
                  </span>
                </button>
              </form>
              <div v-if="washSuccessMessage" class="alert alert-success mt-2" role="alert">
                {{ washSuccessMessage }}
              </div>
              <div v-if="washErrorMessage" class="alert alert-danger mt-2" role="alert">
                {{ washErrorMessage }}
              </div>
            </div>

            <hr />

            <div class="workflow-section">
              <h5>Maintenance Complete</h5>
              <form @submit.prevent="submitMaintenanceComplete">
                <div class="mb-3">
                  <input
                    v-model="completeOrderId"
                    type="text"
                    class="form-control"
                    placeholder="Enter order ID to mark complete"
                    required
                  />
                </div>
                <button type="submit" class="btn btn-success w-100">
                  <span v-if="!isLoadingComplete">Mark Maintenance Complete</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Processing...
                  </span>
                </button>
              </form>
              <div v-if="completeSuccessMessage" class="alert alert-success mt-2" role="alert">
                {{ completeSuccessMessage }}
              </div>
              <div v-if="completeErrorMessage" class="alert alert-danger mt-2" role="alert">
                {{ completeErrorMessage }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Returns -->
      <div class="row g-4 mt-2">
        <div class="col-12">
          <div class="activity-card">
            <h2>Recent Returns</h2>
            <div class="activity-list">
              <div v-if="recentReturns.length === 0" class="text-muted text-center py-4">
                No returns processed yet
              </div>
              <div v-for="returnItem in recentReturns" :key="returnItem.id" class="return-item">
                <div class="return-header">
                  <p class="return-id">Order {{ returnItem.orderId }}</p>
                  <p class="return-fee">Damage Fee: ${{ returnItem.damageFee }}</p>
                </div>
                <p class="return-damage">{{ returnItem.damageReport }}</p>
                <p class="return-time">{{ formatDate(returnItem.timestamp) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminService from '../services/admin'

const orderId = ref('')
const damageReport = ref('')
const damageFee = ref(0)
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const washOrderId = ref('')
const isLoadingWash = ref(false)
const washSuccessMessage = ref('')
const washErrorMessage = ref('')

const completeOrderId = ref('')
const isLoadingComplete = ref(false)
const completeSuccessMessage = ref('')
const completeErrorMessage = ref('')

const recentReturns = ref([])

const submitReturn = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    await AdminService.processReturn({
      order_id: orderId.value,
      damage_report: damageReport.value,
      damage_fee: damageFee.value
    })
    successMessage.value = `Return processed for order ${orderId.value}`

    recentReturns.value.unshift({
      id: Date.now(),
      orderId: orderId.value,
      damageReport: damageReport.value,
      damageFee: damageFee.value,
      timestamp: new Date().toISOString()
    })

    orderId.value = ''
    damageReport.value = ''
    damageFee.value = 0

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to process return'
  } finally {
    isLoading.value = false
  }
}

const submitTransitionToWash = async () => {
  washErrorMessage.value = ''
  washSuccessMessage.value = ''
  isLoadingWash.value = true

  try {
    await AdminService.transitionToWash(washOrderId.value)
    washSuccessMessage.value = `Order ${washOrderId.value} sent to wash`
    washOrderId.value = ''

    setTimeout(() => {
      washSuccessMessage.value = ''
    }, 3000)
  } catch (error) {
    washErrorMessage.value = error.message || 'Failed to transition to wash'
  } finally {
    isLoadingWash.value = false
  }
}

const submitMaintenanceComplete = async () => {
  completeErrorMessage.value = ''
  completeSuccessMessage.value = ''
  isLoadingComplete.value = true

  try {
    await AdminService.maintenanceComplete(completeOrderId.value)
    completeSuccessMessage.value = `Maintenance completed for order ${completeOrderId.value}`
    completeOrderId.value = ''

    setTimeout(() => {
      completeSuccessMessage.value = ''
    }, 3000)
  } catch (error) {
    completeErrorMessage.value = error.message || 'Failed to complete maintenance'
  } finally {
    isLoadingComplete.value = false
  }
}

const formatDate = (dateString) => {
  try {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
    return formatter.format(new Date(dateString))
  } catch {
    return dateString
  }
}
</script>

<style scoped>
.return-container {
  min-height: 100vh;
  padding-top: 100px;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.form-card,
.workflow-card,
.activity-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-card h2,
.workflow-card h2,
.activity-card h2 {
  margin-bottom: 0.5rem;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.75rem;
}

.form-card p,
.workflow-card p,
.activity-card p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.form-label {
  font-weight: 600;
  color: #2b3035;
  margin-bottom: 0.625rem;
}

.form-control,
textarea {
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  padding: 0.75rem;
  background-color: #f6efe1;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus,
textarea:focus {
  background-color: #fff;
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
}

textarea {
  resize: vertical;
}

.btn-primary,
.btn-secondary,
.btn-success {
  font-weight: 700;
  border-radius: 12px;
  padding: 0.75rem;
  transition: background-color 0.2s ease;
  border: none;
}

.btn-primary {
  background-color: #d8a61c;
  color: white;
}

.btn-primary:hover {
  background-color: #c49416;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.workflow-section h5 {
  font-weight: 700;
  color: #2b3035;
  margin-bottom: 1rem;
}

.activity-list {
  max-height: 600px;
  overflow-y: auto;
}

.return-item {
  padding: 1.5rem;
  border: 1px solid #eee;
  border-radius: 12px;
  margin-bottom: 1rem;
  background-color: #fafaf8;
}

.return-item:last-child {
  margin-bottom: 0;
}

.return-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.return-id {
  margin: 0;
  font-weight: 600;
  color: #2b3035;
}

.return-fee {
  margin: 0;
  font-weight: 600;
  color: #d8a61c;
}

.return-damage {
  margin: 0.5rem 0;
  color: #555;
  font-size: 0.95rem;
}

.return-time {
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
  color: #6c757d;
}

.alert {
  border-radius: 12px;
  border: none;
}

.alert-success {
  background-color: #d1e7dd;
  color: #0f5132;
}

.alert-danger {
  background-color: #f8d7da;
  color: #842029;
}

hr {
  margin: 1.5rem 0;
  border: none;
  border-top: 1px solid #eee;
}
</style>
