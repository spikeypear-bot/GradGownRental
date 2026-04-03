<template>
  <div class="return-container">
    <div class="container py-4">
      <div class="mb-4">
        <p class="page-kicker mb-2">Admin Team</p>
        <h2 class="fw-bold mb-2">Process Return</h2>
        <p class="text-muted mb-0">Record the return and attach damage evidence when any item is affected</p>
      </div>

      <div class="row g-4">
        <div class="col-12">
          <div class="reference-card">
            <h2>Damage Deduction Board</h2>
            <div class="table-responsive">
              <table class="table table-sm align-middle compact-table mb-0">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Deduction</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in deductionBoard" :key="item.key">
                    <td>{{ item.label }}</td>
                    <td>{{ item.rateLabel }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-12">
          <div class="form-card">
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
                <label class="form-label">Damaged Items</label>
                <div class="damage-checklist">
                  <label v-for="item in deductionBoard" :key="item.key" class="damage-option">
                    <input
                      v-model="damagedComponents"
                      type="checkbox"
                      :value="item.key"
                    />
                    <span>{{ item.label }}</span>
                    <small>{{ item.rateLabel }}</small>
                  </label>
                </div>
              </div>

              <div class="mb-3">
                <label for="damageReport" class="form-label">Damage Description</label>
                <textarea
                  id="damageReport"
                  v-model="damageReport"
                  class="form-control"
                  rows="4"
                  :placeholder="hasDamage ? 'Describe the damage clearly for the repair team...' : 'No damage notes required for a clean return'"
                  :required="hasDamage"
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="damagePhotos" class="form-label">Damage Photos</label>
                <input
                  id="damagePhotos"
                  type="file"
                  class="form-control"
                  accept="image/*"
                  multiple
                  :required="hasDamage"
                  @change="handleDamageImages"
                />
                <small class="text-muted">Upload one or more photos when damage is reported.</small>
                <div v-if="damageImages.length" class="upload-list mt-2">
                  <div v-for="image in damageImages" :key="image.name + image.size" class="upload-pill">
                    {{ image.name }}
                  </div>
                </div>
              </div>

              <div class="fee-preview">
                <p class="preview-label">Estimated Damage Fee</p>
                <p class="preview-value">SGD ${{ estimatedDamageFee }}</p>
                <small class="text-muted">The saga calculates this automatically from the deposit and damaged items.</small>
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
            <div v-if="returnSummary" class="summary-card mt-3">
              <h6 class="mb-2">Return Summary</h6>
              <p class="mb-1"><strong>Order:</strong> {{ returnSummary.order_id }}</p>
              <p class="mb-1"><strong>Damaged Items:</strong> {{ formatComponents(returnSummary.damaged_components) }}</p>
              <p class="mb-1"><strong>Damage Fee:</strong> SGD ${{ returnSummary.damage_fee }}</p>
              <p class="mb-1"><strong>Refund ID:</strong> {{ returnSummary.refund_id || 'No refund issued' }}</p>
              <p class="mb-0"><strong>Refundable Amount:</strong> SGD ${{ returnSummary.refundable_amount }}</p>
            </div>
            <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">
              {{ errorMessage }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import AdminService from '../services/admin'

const deductionBoard = [
  { key: 'gown', label: 'Gown', rate: 0.6, rateLabel: '60% of deposit' },
  { key: 'hood', label: 'Hood', rate: 0.25, rateLabel: '25% of deposit'},
  { key: 'mortarboard', label: 'Mortarboard', rate: 0.15, rateLabel: '15% of deposit'}
]

const orderId = ref('')
const damageReport = ref('')
const damagedComponents = ref([])
const damageImages = ref([])
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const returnSummary = ref(null)

const hasDamage = computed(() => damagedComponents.value.length > 0)
const estimatedDamageFee = computed(() => {
  const deductionRate = deductionBoard
    .filter(item => damagedComponents.value.includes(item.key))
    .reduce((sum, item) => sum + item.rate, 0)

  return deductionRate === 0 ? '0.00' : 'Auto-calculated after order lookup'
})

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error(`Failed to read ${file.name}`))
    reader.readAsDataURL(file)
  })

const handleDamageImages = async (event) => {
  const files = Array.from(event.target.files || [])
  damageImages.value = files
}

const formatComponents = (components = []) => {
  if (!components.length) return 'No damaged items reported'
  return components
    .map(component => component.charAt(0).toUpperCase() + component.slice(1))
    .join(', ')
}

const submitReturn = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  returnSummary.value = null

  if (hasDamage.value && !damageReport.value.trim()) {
    errorMessage.value = 'Please add a damage description.'
    return
  }

  if (hasDamage.value && damageImages.value.length === 0) {
    errorMessage.value = 'Please upload at least one damage photo.'
    return
  }

  isLoading.value = true

  try {
    const damageImagesPayload = await Promise.all(
      damageImages.value.map(async (file) => ({
        name: file.name,
        type: file.type,
        size: file.size,
        data_url: await readFileAsDataUrl(file)
      }))
    )

    const result = await AdminService.processReturn({
      order_id: orderId.value,
      damage_report: damageReport.value.trim(),
      damaged_components: damagedComponents.value,
      damage_images: damageImagesPayload
    })
    returnSummary.value = result
    successMessage.value = `Return processed for order ${orderId.value}. Refundable amount: SGD $${result.refundable_amount}`

    orderId.value = ''
    damageReport.value = ''
    damagedComponents.value = []
    damageImages.value = []
    const damagePhotos = document.getElementById('damagePhotos')
    if (damagePhotos) damagePhotos.value = ''

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to process return'
  } finally {
    isLoading.value = false
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

.page-kicker {
  color: #8a5f10;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.form-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.summary-card {
  padding: 1rem;
  border-radius: 16px;
  background: #f8f3e7;
  border: 1px solid #eadfbe;
}

.reference-card {
  background: white;
  border-radius: 20px;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.compact-table th,
.compact-table td {
  padding-top: 0.4rem;
  padding-bottom: 0.4rem;
}

.damage-checklist {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 0.75rem;
}

.damage-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border: 1px solid #e0ddd3;
  border-radius: 14px;
  background: #fcfaf5;
}

.damage-option input {
  margin: 0;
}

.damage-option span {
  font-weight: 600;
  color: #2b3035;
}

.damage-option small {
  margin-left: auto;
  color: #7c7467;
}

.upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.upload-pill {
  background: #f2ead8;
  color: #6a5530;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.fee-preview {
  border-radius: 16px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #f7efdf 0%, #fff8ed 100%);
  border: 1px solid #eadfbe;
}

.preview-label {
  margin-bottom: 0.2rem;
  color: #7c7467;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.preview-value {
  margin-bottom: 0.2rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: #8a5f10;
}

.form-card h2,
.reference-card h2 {
  margin-bottom: 0.35rem;
  color: #2b3035;
  font-weight: 700;
  font-size: 1.75rem;
}

.form-card p,
.reference-card p {
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
