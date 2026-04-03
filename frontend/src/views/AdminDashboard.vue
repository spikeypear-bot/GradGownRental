<template>
  <div class="admin-dashboard">
    <div class="container-fluid py-4">
      <div class="row mb-4">
        <div class="col-12">
          <h2 class="fw-bold mb-2">Admin Overview</h2>
          <p class="text-muted">Manage gown rentals, collections, and returns</p>
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="row g-3 mb-5">
        <div class="col-md-3">
          <div class="metric-card pending">
            <div class="metric-icon">
              <i class="bi bi-hourglass-split"></i>
            </div>
            <div class="metric-content">
              <p class="metric-label">Pending Orders</p>
              <p class="metric-value">{{ pendingCount }}</p>
              <RouterLink to="/admin/pending-orders" class="metric-link">View →</RouterLink>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="metric-card active">
            <div class="metric-icon">
              <i class="bi bi-bag-check"></i>
            </div>
            <div class="metric-content">
              <p class="metric-label">Active Rentals</p>
              <p class="metric-value">{{ activeCount }}</p>
              <RouterLink to="/admin/active-orders" class="metric-link">View →</RouterLink>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="metric-card returns">
            <div class="metric-icon">
              <i class="bi bi-inbox"></i>
            </div>
            <div class="metric-content">
              <p class="metric-label">Returns Queue</p>
              <p class="metric-value">{{ returnsCount }}</p>
              <RouterLink to="/admin/returns-queue" class="metric-link">View →</RouterLink>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="metric-card completed">
            <div class="metric-icon">
              <i class="bi bi-check-circle"></i>
            </div>
            <div class="metric-content">
              <p class="metric-label">Completed</p>
              <p class="metric-value">{{ completedCount }}</p>
              <RouterLink to="/admin/orders" class="metric-link">View →</RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow Sections -->
      <div class="row g-4">
        <!-- Fulfillment Workflow -->
        <div class="col-lg-6">
          <div class="workflow-card">
            <div class="workflow-header">
              <h4>
                <i class="bi bi-truck"></i> Fulfillment Workflow
              </h4>
              <span class="badge bg-warning">Scenario 3</span>
            </div>
            <div class="workflow-steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <p class="step-title">Student Places Order</p>
                  <p class="step-desc">Order created in PENDING status</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <p class="step-title">Payment Confirmed</p>
                  <p class="step-desc">Status becomes CONFIRMED</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <p class="step-title">Activate Fulfillment</p>
                  <p class="step-desc">Staff collects/delivers gown</p>
                </div>
              </div>
            </div>
            <RouterLink to="/admin/fulfillment" class="btn btn-primary w-100 mt-3">
              <i class="bi bi-arrow-right"></i> Process Fulfillment
            </RouterLink>
          </div>
        </div>

        <!-- Returns & Maintenance Workflow -->
        <div class="col-lg-6">
          <div class="workflow-card">
            <div class="workflow-header">
              <h4>
                <i class="bi bi-arrow-clockwise"></i> Returns & Maintenance
              </h4>
              <span class="badge bg-danger">Scenario 4</span>
            </div>
            <div class="workflow-steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <p class="step-title">Student Returns Gown</p>
                  <p class="step-desc">Status becomes ACTIVE → RETURNED</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <p class="step-title">Process Damage Report</p>
                  <p class="step-desc">Calculate damage fee & refund</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <p class="step-title">Maintenance Workflow</p>
                  <p class="step-desc">Repair → Wash → Complete</p>
                </div>
              </div>
            </div>
            <RouterLink to="/admin/returns-queue" class="btn btn-danger w-100 mt-3">
              <i class="bi bi-arrow-right"></i> View Returns Queue
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row g-4 mt-3">
        <div class="col-12">
          <div class="quick-actions">
            <h5>Quick Actions</h5>
            <div class="actions-grid">
              <RouterLink to="/admin/pending-orders" class="action-card">
                <i class="bi bi-hourglass-split"></i>
                <span>Confirm Pending Orders</span>
              </RouterLink>
              <RouterLink to="/admin/fulfillment" class="action-card">
                <i class="bi bi-truck"></i>
                <span>Activate Fulfillment</span>
              </RouterLink>
              <RouterLink to="/admin/returns-queue" class="action-card">
                <i class="bi bi-inbox"></i>
                <span>Process Returns</span>
              </RouterLink>
              <RouterLink to="/admin/maintenance" class="action-card">
                <i class="bi bi-wrench"></i>
                <span>Check Maintenance</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { fetchOrdersByStatus } from '../services/admin/helpers'

const orderApiUrl = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'

const pendingCount = ref(0)
const activeCount = ref(0)
const returnsCount = ref(0)
const completedCount = ref(0)

const loadCounts = async () => {
  try {
    const [pending, confirmed, active, returnedDamaged, completed] = await Promise.allSettled([
      fetchOrdersByStatus(orderApiUrl, 'PENDING'),
      fetchOrdersByStatus(orderApiUrl, 'CONFIRMED'),
      fetchOrdersByStatus(orderApiUrl, 'ACTIVE'),
      fetchOrdersByStatus(orderApiUrl, 'RETURNED_DAMAGED'),
      fetchOrdersByStatus(orderApiUrl, 'COMPLETED')
    ])

    pendingCount.value = pending.status === 'fulfilled' ? pending.value.length : 0
    activeCount.value = active.status === 'fulfilled' ? active.value.length : 0
    returnsCount.value = returnedDamaged.status === 'fulfilled' ? returnedDamaged.value.length : 0
    completedCount.value = completed.status === 'fulfilled' ? completed.value.length : 0

    // confirmed is intentionally fetched in case you later want to show "awaiting fulfillment"
    void confirmed
  } catch (error) {
    console.error('Error loading counts:', error)
  }
}

onMounted(() => {
  loadCounts()
  // Refresh every 30 seconds
  setInterval(loadCounts, 30000)
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  padding-top: 100px;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
}

.container-fluid {
  max-width: 1400px;
  margin: 0 auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

/* Metric Cards */
.metric-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 4px solid;
  text-decoration: none;
  color: inherit;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.metric-card.pending {
  border-left-color: #ffc107;
}

.metric-card.active {
  border-left-color: #d8a61c;
}

.metric-card.returns {
  border-left-color: #e74c3c;
}

.metric-card.completed {
  border-left-color: #28a745;
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.metric-card.pending .metric-icon {
  background-color: #ffc107;
}

.metric-card.active .metric-icon {
  background-color: #d8a61c;
}

.metric-card.returns .metric-icon {
  background-color: #e74c3c;
}

.metric-card.completed .metric-icon {
  background-color: #28a745;
}

.metric-content {
  flex: 1;
  margin: 0;
}

.metric-label {
  margin: 0 0 0.5rem 0;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
}

.metric-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #2b3035;
}

.metric-link {
  color: #d8a61c;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  margin-top: 0.5rem;
  display: inline-block;
  transition: color 0.2s ease;
}

.metric-link:hover {
  color: #c49416;
}

/* Workflow Cards */
.workflow-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f0ebe2;
  padding-bottom: 1rem;
}

.workflow-header h4 {
  margin: 0;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-weight: 700;
}

.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step {
  display: flex;
  gap: 1rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f6efe1;
  color: #d8a61c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  margin: 0;
}

.step-title {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  color: #2b3035;
}

.step-desc {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
}

.btn-primary,
.btn-danger {
  font-weight: 700;
  border-radius: 12px;
}

.btn-primary {
  background-color: #d8a61c;
  border-color: #d8a61c;
}

.btn-primary:hover {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-danger {
  background-color: #e74c3c;
  border-color: #e74c3c;
}

.btn-danger:hover {
  background-color: #c9302c;
  border-color: #c9302c;
}

/* Quick Actions */
.quick-actions {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.quick-actions h5 {
  margin: 0 0 1.5rem 0;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1.5rem;
  background-color: #f9f7f2;
  border-radius: 12px;
  text-decoration: none;
  color: #2b3035;
  font-weight: 600;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  background-color: #fff0da;
  border-color: #d8a61c;
  color: #d8a61c;
}

.action-card i {
  font-size: 1.75rem;
}

.action-card span {
  text-align: center;
  font-size: 0.95rem;
}

@media (max-width: 1024px) {
  .admin-dashboard {
    margin-left: 0;
  }
}
</style>
