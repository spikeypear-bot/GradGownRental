<template>
  <div class="return-container">
    <div class="container py-4">
      <div class="page-header">
        <h2 class="fw-bold mb-2">Admin Team</h2>
        <p class="text-muted mb-0">Process returns and record any damage.</p>
        <p v-if="isDemoMode" class="text-warning mb-0 small">Demo mode is on. All active orders are available for return inspection immediately.</p>
      </div>

      <div v-if="successMessage" class="alert alert-success mb-4" role="alert">
        <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-danger mb-4" role="alert">
        <i class="bi bi-exclamation-circle me-2"></i>{{ errorMessage }}
      </div>

      <div v-if="!selectedOrder" class="return-card">
        <div class="card-header-section">
          <div class="d-flex align-items-center gap-2 mb-1">
            <h5 class="mb-0 fw-bold">Return for {{ todayLabel }}</h5>
            <span class="count-badge">{{ returnQueue.length }}</span>
          </div>
        </div>

        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">Loading active returns...</p>
        </div>

        <div v-else-if="returnQueue.length === 0" class="empty-state">
          <i class="bi bi-arrow-return-left"></i>
          <p>No returns scheduled for today.</p>
        </div>

        <div v-else class="return-list">
          <div
            v-for="order in returnQueue"
            :key="order.orderID"
            class="return-row"
          >
            <div class="order-info">
              <span class="order-id">{{ order.orderID }}</span>
              <p class="customer-name mb-0">{{ order.CustomerName }}</p>
            </div>
            <button
              class="btn btn-sm btn-return"
              @click="startInspection(order)"
            >
              Mark as Returned
            </button>
          </div>
        </div>
      </div>

      <div v-else class="inspection-card">
        <div class="inspection-head">
          <div>
            <h5 class="mb-1 fw-bold">Return for {{ todayLabel }}</h5>
            <p class="mb-0 text-muted">{{ selectedOrder.CustomerName }} | {{ selectedOrder.orderID }}</p>
          </div>
          <button class="btn btn-outline-secondary" @click="resetInspection" :disabled="isSubmitting">
            Back
          </button>
        </div>

        <form @submit.prevent="submitReturn">
          <div class="mb-4">
            <label class="section-label">Damage Status</label>
            <div class="choice-grid">
              <label class="choice-card">
                <input v-model="damageSelection" type="radio" value="NO_DAMAGE" />
                <div>
                  <span>No damage</span>
                  <small>Complete the return without a repair report.</small>
                </div>
              </label>
              <label class="choice-card">
                <input v-model="damageSelection" type="radio" value="HAS_DAMAGE" />
                <div>
                  <span>Damage found</span>
                  <small>Send the order into repair with evidence attached.</small>
                </div>
              </label>
            </div>
          </div>

          <div v-if="hasDamage" class="damage-section">
            <div class="mb-4">
              <label class="section-label">Damaged Items</label>
              <div class="damage-checklist">
                <label
                  v-for="item in damageOptions"
                  :key="item.key"
                  class="damage-option"
                  :class="{ 'damage-option--disabled': !orderComponentKeys.has(item.key) }"
                >
                  <input
                    v-model="damagedComponents"
                    type="checkbox"
                    :value="item.key"
                    :disabled="!orderComponentKeys.has(item.key)"
                  />
                  <span>{{ item.label }}</span>
                </label>
              </div>
            </div>

            <div class="mb-4">
              <label for="damageReport" class="section-label">Damage Description</label>
              <textarea
                id="damageReport"
                v-model="damageReport"
                class="form-control"
                rows="4"
                placeholder="Describe the damage clearly for the repair team..."
                :required="hasDamage"
              ></textarea>
            </div>

            <div class="mb-4">
              <label for="damagePhotos" class="section-label">Attach Evidence</label>
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
          </div>

          <button type="submit" class="btn btn-return w-100" :disabled="isSubmitting">
            <span v-if="!isSubmitting">Submit Return</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              Processing...
            </span>
          </button>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdminService from '../services/admin'
import { fetchOrdersByStatus } from '../services/admin/helpers'
import { isDemoMode } from '../config/demoMode'
import { readMaintenanceDetails, writeMaintenanceDetails } from '../services/admin/maintenance'

const damageOptions = [
  { key: 'gown', label: 'Gown' },
  { key: 'hood', label: 'Hood' },
  { key: 'mortarboard', label: 'Mortarboard' }
]

const orders = ref([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const selectedOrder = ref(null)
const damageSelection = ref('NO_DAMAGE')
const damagedComponents = ref([])
const damageReport = ref('')
const damageImages = ref([])
const successMessage = ref('')
const errorMessage = ref('')

function formatDateKey(dateInput) {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Singapore',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
  return formatter.format(new Date(dateInput))
}

const todayKey = computed(() => formatDateKey(new Date()))

const todayLabel = computed(() => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'Asia/Singapore',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(new Date())
  } catch {
    return String(new Date())
  }
})

const returnQueue = computed(() =>
  orders.value.filter(order => isDemoMode || formatDateKey(order.rental_end_date) === todayKey.value)
)

const hasDamage = computed(() => damageSelection.value === 'HAS_DAMAGE')

const orderComponentKeys = computed(() => {
  if (!selectedOrder.value) return new Set()
  return new Set(
    (selectedOrder.value.selected_items || [])
      .map(item => getComponentKeyForItem(item))
      .filter(Boolean)
  )
})

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error(`Failed to read ${file.name}`))
    reader.readAsDataURL(file)
  })

const getComponentKeyForItem = (item = {}) => {
  const raw = String(item.itemType || item.item_type || item.itemName || item.item_name || '').toLowerCase()
  if (raw.includes('gown')) return 'gown'
  if (raw.includes('hood')) return 'hood'
  if (raw.includes('hat') || raw.includes('mortarboard') || raw.includes('cap')) return 'mortarboard'
  return null
}

const loadActiveReturns = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const orderApiUrl =
      import.meta.env.VITE_ORDER_API_BASE_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'
    orders.value = await fetchOrdersByStatus(orderApiUrl, 'ACTIVE')
  } catch (error) {
    console.error('Error loading active returns:', error)
    errorMessage.value = error.message || 'Failed to load active returns'
  } finally {
    isLoading.value = false
  }
}

const startInspection = (order) => {
  selectedOrder.value = order
  damageSelection.value = 'NO_DAMAGE'
  damagedComponents.value = []
  damageReport.value = ''
  damageImages.value = []
  errorMessage.value = ''
}

const resetInspection = () => {
  selectedOrder.value = null
  damageSelection.value = 'NO_DAMAGE'
  damagedComponents.value = []
  damageReport.value = ''
  damageImages.value = []
  const damagePhotos = document.getElementById('damagePhotos')
  if (damagePhotos) damagePhotos.value = ''
}

const handleDamageImages = (event) => {
  damageImages.value = Array.from(event.target.files || [])
}

const submitReturn = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!selectedOrder.value) {
    errorMessage.value = 'Please choose an order to return.'
    return
  }

  if (hasDamage.value && damagedComponents.value.length === 0) {
    errorMessage.value = 'Please select at least one damaged item.'
    return
  }

  if (hasDamage.value && !damageReport.value.trim()) {
    errorMessage.value = 'Please add a damage description.'
    return
  }

  if (hasDamage.value && damageImages.value.length === 0) {
    errorMessage.value = 'Please upload at least one damage photo.'
    return
  }

  isSubmitting.value = true

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
      order_id: selectedOrder.value.orderID,
      selected_packages: (Array.isArray(selectedOrder.value.selected_items) ? selectedOrder.value.selected_items : []).map(item => ({
        ...item,
        chosenDate: item.chosenDate || selectedOrder.value.rental_start_date
      })),
      damage_report: hasDamage.value ? damageReport.value.trim() : '',
      damaged_components: hasDamage.value ? damagedComponents.value : [],
      damage_images: hasDamage.value ? damageImagesPayload : []
    })

    const allSelected = Array.isArray(selectedOrder.value.selected_items)
      ? selectedOrder.value.selected_items
      : []
    const damagedSet = new Set(hasDamage.value ? damagedComponents.value : [])
    const sagaDamagedPackages = Array.isArray(result?.damaged_packages) ? result.damaged_packages : []
    const damagedPackages = sagaDamagedPackages.length
      ? sagaDamagedPackages
      : allSelected.filter(item => damagedSet.has(getComponentKeyForItem(item)))
    const cleanPackages = allSelected.filter(item => !damagedSet.has(getComponentKeyForItem(item)))
    const damagedItemStages = Object.fromEntries(
      damagedPackages.map(item => [
        item.damageId ? `damage-${item.damageId}` : [item.modelId, item.qty || 1, item.chosenDate || ''].join(':'),
        'repair'
      ])
    )
    const cleanItemStages = Object.fromEntries(
      cleanPackages.map(item => [
        [item.modelId, item.qty || 1, item.chosenDate || ''].join(':'),
        'wash'
      ])
    )
    const detailsMap = readMaintenanceDetails()
    detailsMap[selectedOrder.value.orderID] = {
      allSelected,
      damagedPackages,
      cleanPackages,
      damagedItemStages,
      cleanItemStages,
    }
    writeMaintenanceDetails(detailsMap)

    successMessage.value = `Return processed for order ${selectedOrder.value.orderID}.`
    orders.value = orders.value.filter(order => order.orderID !== selectedOrder.value.orderID)
    resetInspection()

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to process return'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadActiveReturns)
</script>

<style scoped>
.return-container {
  min-height: 100vh;
  background-color: #fbf7ef;
  padding-bottom: 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.return-card,
.inspection-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0ddd3;
  margin-bottom: 1rem;
}

.inspection-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0ddd3;
  margin-bottom: 1.5rem;
}

.count-badge {
  margin-left: auto;
  background-color: #d8a61c;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 10px;
  font-weight: 700;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #aaa;
}

.empty-state i {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
  color: #d8a61c;
  opacity: 0.4;
}

.return-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.return-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background-color: #f9f7f2;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}

.return-row:hover {
  background-color: #f3eedf;
}

.order-info {
  flex: 1;
  min-width: 0;
}

.order-id {
  font-size: 0.82rem;
  font-weight: 700;
  color: #999;
  display: block;
  word-break: break-all;
}

.customer-name {
  font-weight: 600;
  color: #2b3035;
  font-size: 0.95rem;
}

.section-label {
  display: block;
  margin-bottom: 0.75rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #7c7467;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.choice-card,
.damage-option {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid #e0ddd3;
  border-radius: 14px;
  background: #fcfaf5;
}

.choice-card input,
.damage-option input {
  margin-top: 0.2rem;
}

.choice-card span,
.damage-option span {
  display: block;
  font-weight: 700;
  color: #2b3035;
}

.choice-card small {
  display: block;
  color: #7c7467;
  margin-top: 0.25rem;
}

.damage-checklist {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.damage-option--disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.damage-option--disabled input {
  cursor: not-allowed;
}

.damage-option--disabled span {
  color: #aaa;
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

.btn-return {
  background-color: #d8a61c;
  border-color: #d8a61c;
  color: white;
  border-radius: 10px;
  font-weight: 700;
}

.btn-return:hover:not(:disabled) {
  background-color: #c49416;
  border-color: #c49416;
  color: white;
}

.btn-outline-secondary {
  border-radius: 10px;
  font-weight: 600;
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

@media (max-width: 768px) {
  .inspection-head,
  .return-row {
    flex-direction: column;
    align-items: stretch;
  }

  .choice-grid,
  .damage-checklist {
    grid-template-columns: 1fr;
  }
}
</style>
