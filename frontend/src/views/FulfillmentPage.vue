<template>
  <div class="fulfillment-container">
    <div class="container py-4">
      <div class="row g-4">
        <!-- Fulfillment Form -->
        <div class="col-lg-6">
          <div class="form-card">
            <h2>Activate Fulfillment</h2>
            <p class="text-muted">Process gown collection and delivery handovers</p>

            <form @submit.prevent="submitFulfillment">
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

              <button type="submit" class="btn btn-primary w-100">
                <span v-if="!isLoading">Activate Fulfillment</span>
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

        <!-- Recent Activity -->
        <div class="col-lg-6">
          <div class="activity-card">
            <h2>Recent Activity</h2>
            <div class="activity-list">
              <div v-if="recentActivities.length === 0" class="text-muted text-center py-4">
                No fulfillment activities yet
              </div>
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <div class="activity-icon">
                  <i class="bi bi-check-circle"></i>
                </div>
                <div class="activity-content">
                  <p class="activity-title">Order {{ activity.orderId }}</p>
                  <p class="activity-time">{{ formatDate(activity.timestamp) }}</p>
                </div>
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
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const recentActivities = ref([])

const submitFulfillment = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    await AdminService.activateFulfillment(orderId.value)
    successMessage.value = `Fulfillment activated for order ${orderId.value}`

    recentActivities.value.unshift({
      id: Date.now(),
      orderId: orderId.value,
      timestamp: new Date().toISOString()
    })

    orderId.value = ''

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to activate fulfillment'
  } finally {
    isLoading.value = false
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
.fulfillment-container {
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
.activity-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-card h2,
.activity-card h2 {
  margin-bottom: 0.5rem;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.75rem;
}

.form-card p,
.activity-card p {
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.form-label {
  font-weight: 600;
  color: #2b3035;
  margin-bottom: 0.625rem;
}

.form-control {
  border: 1px solid #e0ddd3;
  border-radius: 12px;
  padding: 0.75rem;
  background-color: #f6efe1;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
  background-color: #fff;
  border-color: #d8a61c;
  box-shadow: 0 0 0 3px rgba(216, 166, 28, 0.1);
}

.btn-primary {
  background-color: #d8a61c;
  border-color: #d8a61c;
  font-weight: 700;
  border-radius: 12px;
  padding: 0.75rem;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #c49416;
  border-color: #c49416;
}

.activity-list {
  max-height: 500px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background-color: #fafaf8;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.5rem;
  color: #d8a61c;
  margin-right: 1rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
  margin: 0;
}

.activity-title {
  margin: 0;
  font-weight: 600;
  color: #2b3035;
}

.activity-time {
  margin: 0.25rem 0 0 0;
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
</style>
