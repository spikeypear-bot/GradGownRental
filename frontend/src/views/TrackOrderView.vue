<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import orderService from '@/services/order'
import inventoryService from '@/services/inventory'

const route = useRoute()
const orderId = ref((route.query.orderId || '').toString())
const loading = ref(false)
const actionLoading = ref(false)
const error = ref('')
const success = ref('')
const order = ref(null)
const packageDetail = ref(null)

const damagedItems = ref([{ modelId: '', qty: 1 }])

const canActivate = computed(() => {
  return order.value && order.value.status === 'CONFIRMED' && order.value.fulfillment_method === 'COLLECTION'
})

const canReturn = computed(() => {
  return order.value && order.value.status === 'ACTIVE'
})

const selectedItems = computed(() => {
  if (!Array.isArray(order.value?.selected_items)) return []
  return order.value.selected_items
})

const packageTitle = computed(() => {
  if (!packageDetail.value) return ''
  return `${packageDetail.value.institution} - ${packageDetail.value.educationLevel}`
})

const packageSubtitle = computed(() => {
  if (!packageDetail.value?.educationLevel) return ''
  return `${packageDetail.value.educationLevel} Collection`
})

const selectedItemDetails = computed(() => {
  const styleBuckets = [
    packageDetail.value?.hatStyle,
    packageDetail.value?.hoodStyle,
    packageDetail.value?.gownStyle,
  ].filter(Boolean)

  return selectedItems.value.map((item) => {
    const bucket = styleBuckets.find(style =>
      (style.models || []).some(model => model.modelId === item.modelId)
    )
    const model = bucket?.models?.find(entry => entry.modelId === item.modelId)
    const style = bucket?.inventoryStyle

    return {
      ...item,
      itemName: style?.itemName || `Model ${item.modelId}`,
      itemType: style?.itemType || '',
      size: model?.size || item.size || '',
    }
  })
})

const parsedDamagedItems = computed(() => {
  return damagedItems.value
    .map(item => ({
      modelId: String(item.modelId || '').trim(),
      qty: Number(item.qty || 0)
    }))
    .filter(item => item.modelId && item.qty > 0)
})

const trackOrder = async () => {
  if (!orderId.value.trim()) {
    error.value = 'Please enter an order ID.'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''
  order.value = null
  packageDetail.value = null
  try {
    order.value = await orderService.getOrder(orderId.value.trim())
    if (order.value?.package_id) {
      packageDetail.value = await inventoryService.getPackageById(order.value.package_id)
    }
  } catch (err) {
    error.value = err.message || 'Unable to fetch order.'
  } finally {
    loading.value = false
  }
}

const activateOrder = async () => {
  if (!order.value?.order_id) return

  actionLoading.value = true
  error.value = ''
  success.value = ''
  try {
    order.value = await orderService.activateOrder(order.value.order_id)
    success.value = `Order ${order.value.order_id} is now ACTIVE.`
  } catch (err) {
    error.value = err.message || 'Unable to activate order.'
  } finally {
    actionLoading.value = false
  }
}

const processReturn = async () => {
  if (!order.value?.order_id) return

  actionLoading.value = true
  error.value = ''
  success.value = ''
  try {
    order.value = await orderService.returnOrder(order.value.order_id, parsedDamagedItems.value)
    success.value = `Order ${order.value.order_id} return processed with status ${order.value.status}.`
  } catch (err) {
    error.value = err.message || 'Unable to process return.'
  } finally {
    actionLoading.value = false
  }
}

const addDamagedRow = () => {
  damagedItems.value.push({ modelId: '', qty: 1 })
}

const removeDamagedRow = (idx) => {
  damagedItems.value.splice(idx, 1)
  if (damagedItems.value.length === 0) {
    damagedItems.value.push({ modelId: '', qty: 1 })
  }
}

if (orderId.value.trim()) {
  trackOrder()
}

function formatDate(value) {
  if (!value) return '-'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleDateString('en-US', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <section class="track-page py-5">
    <div class="container" style="max-width: 860px;">
      <h2 class="fw-bold text-dark mb-3">Track My Order</h2>
      <p class="text-secondary mb-4">Track order status and process lifecycle actions for pickup and return.</p>

      <div class="card border-0 shadow-sm rounded-4 p-4 mb-4">
        <div class="d-flex gap-2">
          <input
            v-model="orderId"
            class="form-control form-control-lg"
            placeholder="e.g. ORD-1234 or UUID"
            @keyup.enter="trackOrder"
          />
          <button class="btn btn-warning text-white fw-bold px-4" :disabled="loading" @click="trackOrder">
            {{ loading ? 'Loading...' : 'Track' }}
          </button>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div v-if="order" class="card border-0 shadow-sm rounded-4 p-4 mb-4">
        <h5 class="fw-bold mb-3">Order {{ order.order_id }}</h5>
        <div class="row g-2">
          <div class="col-md-6"><strong>Status:</strong> {{ order.status }}</div>
          <div class="col-md-6"><strong>Fulfillment:</strong> {{ order.fulfillment_method }}</div>
          <div class="col-md-6"><strong>Name:</strong> {{ order.student_name }}</div>
          <div class="col-md-6"><strong>Email:</strong> {{ order.email }}</div>
          <div class="col-md-6"><strong>Rental Date:</strong> {{ formatDate(order.rental_start_date) }}</div>
          <div class="col-md-6"><strong>Return Date:</strong> {{ formatDate(order.rental_end_date) }}</div>
          <div class="col-12"><strong>Total:</strong> ${{ Number(order.total_amount || 0).toFixed(2) }}</div>
        </div>

        <hr />
        <h6 class="fw-bold mb-1">Selected Package</h6>
        <div v-if="packageTitle" class="mb-3">
          <div class="fw-bold">{{ packageTitle }}</div>
          <div class="text-secondary small">{{ packageSubtitle }}</div>
        </div>
        <h6 class="fw-bold mb-2">Selected Items</h6>
        <div v-if="selectedItemDetails.length === 0" class="text-secondary small">No selected items found.</div>
        <ul v-else class="mb-0">
          <li v-for="(item, idx) in selectedItemDetails" :key="`${item.modelId}-${idx}`">
            {{ item.itemName }}<span v-if="item.size"> ({{ item.size }})</span> x {{ item.qty }}
          </li>
        </ul>
      </div>

      <div v-if="order && canActivate" class="card border-0 shadow-sm rounded-4 p-4 mb-4">
        <h6 class="fw-bold">Scenario 3: Activate Collection Order</h6>
        <p class="text-secondary mb-3">When the student picks up in-store, set the order to ACTIVE.</p>
        <button class="btn btn-warning text-white fw-bold" :disabled="actionLoading" @click="activateOrder">
          {{ actionLoading ? 'Processing...' : 'Mark as Collected (Activate)' }}
        </button>
      </div>

      <div v-if="order && canReturn" class="card border-0 shadow-sm rounded-4 p-4">
        <h6 class="fw-bold">Scenario 4: Process Return</h6>
        <p class="text-secondary mb-3">Add damaged items if any, then process return.</p>

        <div class="mb-3">
          <div class="row g-2 align-items-center mb-2" v-for="(row, idx) in damagedItems" :key="idx">
            <div class="col-md-7">
              <input
                v-model="row.modelId"
                class="form-control"
                placeholder="Model ID (leave blank if no damage)"
              />
            </div>
            <div class="col-md-3">
              <input
                v-model.number="row.qty"
                type="number"
                min="1"
                class="form-control"
                placeholder="Qty"
              />
            </div>
            <div class="col-md-2 d-grid">
              <button class="btn btn-outline-secondary" @click="removeDamagedRow(idx)">Remove</button>
            </div>
          </div>
          <button class="btn btn-outline-dark btn-sm" @click="addDamagedRow">Add Row</button>
        </div>

        <button class="btn btn-warning text-white fw-bold" :disabled="actionLoading" @click="processReturn">
          {{ actionLoading ? 'Processing...' : 'Process Return' }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.track-page {
  background-color: #fbf7ef;
  min-height: calc(100vh - 84px);
}
</style>
