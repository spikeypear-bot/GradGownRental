<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import inventoryService from '@/services/inventory'
import orderService from '@/services/order'

const router = useRouter()
const route = useRoute()
const CART_STORAGE_KEY = 'gradgownrental_cart_session'

function parseSelectedModels(rawValue) {
  if (!rawValue) return []
  try {
    const parsed = JSON.parse(String(rawValue))
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function parseISODate(rawValue) {
  if (!rawValue) return null
  const [year, month, day] = String(rawValue).split('-').map(Number)
  if (!year || !month || !day) return null
  return new Date(year, month - 1, day)
}

const selectedSizes = ref({})   // { [itemType]: modelId } — for direct (non-cart) checkout
const fulfillment = ref('pickup')
const currentStep = ref(1)
const isPaymentConfirmed = ref(false)
const confirmedOrderId = ref('')
const isReviewLoading = ref(false)
const isSubmittingPayment = ref(false)
const reviewError = ref('')
const paymentError = ref('')
const stripeError = ref('')
const stripePublicKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || ''
const PAYMENT_API_BASE_URL = import.meta.env.VITE_PAYMENT_API_BASE_URL || 'http://localhost:8000/api/payment'

let stripe = null
let elements = null
let cardElement = null

const holdId = ref('')
const orderId = ref('')

const packageLoading = ref(false)
const packageError = ref('')
const packageDetail = ref(null)
const cartCheckoutItems = ref([])
const cartPackageDetails = ref([])

const contact = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
})

const preselectedModels = ref(parseSelectedModels(route.query.models))

const isCartCheckout = computed(() => String(route.query.cartCheckout || '') === 'true')
const hasPreselectedCheckout = computed(() =>
  !isCartCheckout.value && Boolean(route.query.date) && preselectedModels.value.length > 0,
)
const packageId = computed(() => Number(route.query.packageId || 0))
const primaryPackageId = computed(() => {
  if (isCartCheckout.value) {
    return Number(cartCheckoutItems.value[0]?.packageId || 0)
  }
  return packageId.value
})
const packageTitle = computed(() => {
  if (isCartCheckout.value) {
    if (!cartCheckoutItems.value.length) return 'Cart Checkout'
    if (cartCheckoutItems.value.length === 1) return cartCheckoutItems.value[0].title
    return `${cartCheckoutItems.value.length} Packages`
  }
  if (packageDetail.value) {
    return `${packageDetail.value.institution} - ${packageDetail.value.educationLevel}`
  }
  return route.query.title || 'Graduation Package'
})
const packageLevel = computed(() => {
  if (isCartCheckout.value) return 'Mixed'
  return packageDetail.value?.educationLevel || route.query.level || ''
})

const rentalFee = computed(() => {
  if (isCartCheckout.value) {
    return cartCheckoutItems.value.reduce(
      (sum, item) => sum + Number(item.rentalFee || item.price || 0),
      0,
    )
  }
  return Number(
    packageDetail.value?.totalRentalFee || route.query.rentalFee || route.query.price || 0,
  )
})
const depositFee = computed(() => {
  if (isCartCheckout.value) {
    return cartCheckoutItems.value.reduce((sum, item) => sum + Number(item.deposit || 0), 0)
  }
  return Number(packageDetail.value?.totalDeposit || route.query.deposit || 0)
})
const deliveryFee = computed(() => (fulfillment.value === 'delivery' ? 5 : 0))
const totalCharge = computed(() => rentalFee.value + depositFee.value + deliveryFee.value)
const totalCost = computed(() => totalCharge.value)


// Per-item size options for direct (non-cart) checkout
const sizeOptions = computed(() => {
  if (!packageDetail.value) return []
  return [packageDetail.value.hatStyle, packageDetail.value.hoodStyle, packageDetail.value.gownStyle]
    .filter(Boolean)
    .map(bucket => ({
      itemType: bucket.inventoryStyle?.itemType,
      itemName: bucket.inventoryStyle?.itemName,
      models: (bucket.models || []).map(m => ({
        modelId: m.modelId,
        size: String(m.size || '').toUpperCase(),
        totalQty: m.totalQty
      }))
    }))
})

function applyPreselectedSelections() {
  if (!preselectedModels.value.length) return
  const nextSelections = { ...selectedSizes.value }
  preselectedModels.value.forEach((model) => {
    if (model?.itemType && model?.modelId) {
      nextSelections[model.itemType] = model.modelId
    }
  })
  selectedSizes.value = nextSelections
}

// When packageDetail loads, default selectedSizes to first size of each item
watch(sizeOptions, (options) => {
  if (!options.length) { selectedSizes.value = {}; return }
  const sortOrder = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
  const defaults = {}
  options.forEach(item => {
    const sorted = [...item.models].sort((a, b) => {
      const ai = sortOrder.indexOf(a.size), bi = sortOrder.indexOf(b.size)
      if (ai === -1 && bi === -1) return a.size.localeCompare(b.size)
      if (ai === -1) return 1; if (bi === -1) return -1
      return ai - bi
    })
    if (sorted[0] && !selectedSizes.value[item.itemType]) {
      defaults[item.itemType] = sorted[0].modelId
    }
  })
  selectedSizes.value = { ...defaults, ...selectedSizes.value }
  applyPreselectedSelections()
}, { immediate: true })

watch(currentStep, async (step) => {
  if (step === 4) {
    await nextTick()
    await initStripeCardElement()
  }
})

const today = new Date()
const todayNoTime = new Date(today.getFullYear(), today.getMonth(), today.getDate())
const maxDate = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000)
maxDate.setHours(0, 0, 0, 0)

const viewDate = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const selectedFullDate = ref(null)

const fulfillmentDateISO = computed(() => {
  if (!selectedFullDate.value) return ''
  return toISODate(selectedFullDate.value)
})

const returnDateISO = computed(() => {
  if (!selectedFullDate.value) return ''
  const end = new Date(selectedFullDate.value)
  end.setDate(end.getDate() + 2)
  return toISODate(end)
})

const selectedItemsForBooking = computed(() => {
  if (!selectedFullDate.value) return []
  const chosenDate = fulfillmentDateISO.value

  if (isCartCheckout.value) {
    const aggregated = []
    for (const entry of cartPackageDetails.value) {
      // New format: entry.selectedModels = [{ itemType, itemName, modelId, size }]
      const selectedModels = entry.selectedModels || []
      const styleBuckets = [
        entry.detail?.hatStyle,
        entry.detail?.hoodStyle,
        entry.detail?.gownStyle,
      ].filter(Boolean)

      for (const sel of selectedModels) {
        // Find the matching bucket to get rentalFee/deposit
        const bucket = styleBuckets.find(b => b.inventoryStyle?.itemType === sel.itemType)
        const style = bucket?.inventoryStyle || {}
        aggregated.push({
          modelId: sel.modelId,
          qty: 1,
          chosenDate,
          size: sel.size,
          itemType: sel.itemType,
          itemName: sel.itemName,
          styleId: style.styleId,
          rentalFee: Number(style.rentalFee || 0),
          deposit: Number(style.deposit || 0),
        })
      }
    }
    return aggregated
  }

  // Direct checkout — use selectedSizes map
  return sizeOptions.value
    .map(item => {
      const modelId = selectedSizes.value[item.itemType]
      if (!modelId) return null
      const model = item.models.find(m => m.modelId === modelId)
      const bucket = [packageDetail.value?.hatStyle, packageDetail.value?.hoodStyle, packageDetail.value?.gownStyle]
        .filter(Boolean).find(b => b.inventoryStyle?.itemType === item.itemType)
      const style = bucket?.inventoryStyle || {}
      return {
        modelId,
        qty: 1,
        chosenDate,
        size: model?.size || '',
        itemType: item.itemType,
        itemName: item.itemName,
        styleId: style.styleId,
        rentalFee: Number(style.rentalFee || 0),
        deposit: Number(style.deposit || 0),
      }
    })
    .filter(Boolean)
})

const selectedItemSummary = computed(() =>
  selectedItemsForBooking.value.map((item) => ({
    key: `${item.itemType}-${item.modelId}`,
    itemName: item.itemName || item.itemType,
    size: item.size || '',
    qty: item.qty,
  })),
)

const canProceedStep1 = computed(() => {
  if (isCartCheckout.value) {
    return Boolean(
      cartCheckoutItems.value.length &&
      selectedFullDate.value &&
      selectedItemsForBooking.value.length > 0,
    )
  }
  const allSizesChosen = sizeOptions.value.length > 0 &&
    sizeOptions.value.every(item => Boolean(selectedSizes.value[item.itemType]))
  return Boolean(
    packageDetail.value &&
    selectedFullDate.value &&
    allSizesChosen &&
    selectedItemsForBooking.value.length === sizeOptions.value.length,
  )
})

const isContactValid = computed(() => {
  return (
    contact.value.firstName.trim() !== '' &&
    contact.value.lastName.trim() !== '' &&
    /^\S+@\S+\.\S+$/.test(contact.value.email) &&
    /^[+\d][\d\s-]{6,}$/.test(contact.value.phone.trim())
  )
})

const isSelectedDateToday = computed(() => {
  if (!selectedFullDate.value) return false
  const selectedDateNoTime = new Date(
    selectedFullDate.value.getFullYear(),
    selectedFullDate.value.getMonth(),
    selectedFullDate.value.getDate(),
  )
  return selectedDateNoTime.getTime() === todayNoTime.getTime()
})

const isDeliveryDisabled = computed(() => {
  const disabled = isSelectedDateToday.value
  if (disabled && fulfillment.value === 'delivery') {
    fulfillment.value = 'pickup'
  }
  return disabled
})

const canGoPrev = computed(
  () => viewDate.value > new Date(today.getFullYear(), today.getMonth(), 1),
)

const canGoNext = computed(() => {
  const currentViewYear = viewDate.value.getFullYear()
  const currentViewMonth = viewDate.value.getMonth()
  const maxYear = maxDate.getFullYear()
  const maxMonth = maxDate.getMonth()

  if (currentViewYear < maxYear) return true
  if (currentViewYear === maxYear && currentViewMonth < maxMonth) return true
  return false
})

const viewingMonthYear = computed(() => {
  return viewDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const year = viewDate.value.getFullYear()
  const month = viewDate.value.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()

  const days = []
  for (let i = 0; i < firstDay; i++) {
    days.push({ empty: true })
  }
  for (let i = 1; i <= daysInMonth; i++) {
    const thisDate = new Date(year, month, i)
    const isDisabled = thisDate < todayNoTime || thisDate > maxDate
    days.push({
      empty: false,
      date: i,
      fullDate: thisDate,
      disabled: isDisabled,
    })
  }
  return days
})

const formattedStartDate = computed(() =>
  selectedFullDate.value ? formatDate(selectedFullDate.value) : '',
)
const formattedEndDate = computed(() => {
  if (!selectedFullDate.value) return ''
  const end = new Date(selectedFullDate.value)
  end.setDate(end.getDate() + 2)
  return formatDate(end)
})
const backButtonLabel = computed(() => {
  const firstAvailableStep = hasPreselectedCheckout.value ? 2 : 1
  return currentStep.value === firstAvailableStep ? 'Back to Details' : 'Back to Configuration'
})

onMounted(async () => {
  packageLoading.value = true
  try {
    if (hasPreselectedCheckout.value) {
      selectedFullDate.value = parseISODate(route.query.date)
      if (selectedFullDate.value) {
        viewDate.value = new Date(
          selectedFullDate.value.getFullYear(),
          selectedFullDate.value.getMonth(),
          1,
        )
      }
      currentStep.value = 2
    }

    if (isCartCheckout.value) {
      const raw = localStorage.getItem(CART_STORAGE_KEY)
      const parsed = raw ? JSON.parse(raw) : null
      const expiresAt = Number(parsed?.expiresAt || 0)
      const items = Array.isArray(parsed?.items) ? parsed.items : []
      if (!items.length || expiresAt <= Date.now()) {
        throw new Error('Cart session expired. Please add items again.')
      }
      cartCheckoutItems.value = items

      const uniquePackageIds = [
        ...new Set(items.map((item) => Number(item.packageId)).filter(Boolean)),
      ]
      const detailMap = new Map()
      await Promise.all(
        uniquePackageIds.map(async (id) => {
          const detail = await inventoryService.getPackageById(id)
          detailMap.set(id, detail)
        }),
      )
      cartPackageDetails.value = items
        .map((item) => ({
          ...item,
          detail: detailMap.get(Number(item.packageId)),
        }))
        .filter((entry) => Boolean(entry.detail))
    } else {
      if (!packageId.value) {
        throw new Error('Missing package ID. Please select a package again.')
      }
      packageDetail.value = await inventoryService.getPackageById(packageId.value)
      applyPreselectedSelections()
    }
  } catch (err) {
    packageError.value = err.message || 'Failed to load package details.'
  } finally {
    packageLoading.value = false
  }
})

onBeforeUnmount(() => {
  if (cardElement) {
    cardElement.destroy()
  }
})

const prevMonth = () => {
  if (canGoPrev.value) {
    viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() - 1, 1)
  }
}

const nextMonth = () => {
  if (canGoNext.value) {
    viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + 1, 1)
  }
}

const goBack = () => {
  const firstAvailableStep = hasPreselectedCheckout.value ? 2 : 1
  if (currentStep.value > firstAvailableStep) {
    currentStep.value--
  } else {
    router.back()
  }
}

const goToReview = async () => {
  reviewError.value = ''
  isReviewLoading.value = true
  try {
    const softlockItems = selectedItemsForBooking.value.map((item) => ({
      modelId: item.modelId,
      qty: item.qty,
      chosenDate: item.chosenDate,
    }))
    const hold = await inventoryService.softLockItems(softlockItems)
    holdId.value = hold.holdId

    const studentName = `${contact.value.firstName} ${contact.value.lastName}`.trim()
    const orderInit = await orderService.createOrder({
      hold_id: holdId.value,
      selected_packages: selectedItemsForBooking.value,
      fulfillment_method: fulfillment.value === 'delivery' ? 'DELIVERY' : 'COLLECTION',
      student_name: studentName,
      phone: contact.value.phone.trim(),
      email: contact.value.email.trim(),
      fulfillment_date: fulfillmentDateISO.value,
      return_date: returnDateISO.value,
      total_amount: totalCharge.value.toFixed(2),
      package_id: primaryPackageId.value,
    })

    orderId.value = orderInit.order_id
    currentStep.value = 4
  } catch (err) {
    reviewError.value = err.message || 'Failed to prepare checkout. Please try again.'
  } finally {
    isReviewLoading.value = false
  }
}

const confirmPayment = async () => {
  if (!orderId.value || !holdId.value) return

  paymentError.value = ''
  stripeError.value = ''
  isSubmittingPayment.value = true
  try {
    await initStripeCardElement()
    if (!stripe || !cardElement) {
      throw new Error('Stripe is not ready. Please check publishable key.')
    }

    const intentResponse = await fetch(`${PAYMENT_API_BASE_URL}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: Number(totalCharge.value.toFixed(2)) }),
    })
    const intentPayload = await intentResponse.json()
    const clientSecret = intentPayload?.client_secret
    if (!intentResponse.ok || !clientSecret) {
      throw new Error(intentPayload?.error || 'Failed to create payment intent.')
    }

    const billingName = `${contact.value.firstName} ${contact.value.lastName}`.trim()
    const confirmation = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
        billing_details: {
          name: billingName,
          email: contact.value.email.trim(),
          phone: contact.value.phone.trim(),
        },
      },
    })
    if (confirmation.error) {
      throw new Error(confirmation.error.message || 'Card payment failed.')
    }

    const paymentIntent = confirmation.paymentIntent
    if (!paymentIntent || paymentIntent.status !== 'succeeded') {
      throw new Error(`Payment did not succeed (status=${paymentIntent?.status || 'unknown'}).`)
    }

    const studentName = `${contact.value.firstName} ${contact.value.lastName}`.trim()
    const summary = await orderService.submitPayment({
      order_id: orderId.value,
      hold_id: holdId.value,
      selected_packages: selectedItemsForBooking.value,
      fulfillment_method: fulfillment.value === 'delivery' ? 'DELIVERY' : 'COLLECTION',
      payment_details: {
        method: 'CARD',
        payer_email: contact.value.email.trim(),
        payment_intent_id: paymentIntent.id,
        client_secret: paymentIntent.client_secret,
      },
      student_name: studentName,
      phone: contact.value.phone.trim(),
      email: contact.value.email.trim(),
      fulfillment_date: fulfillmentDateISO.value,
      return_date: returnDateISO.value,
      total_amount: totalCharge.value.toFixed(2),
      package_id: primaryPackageId.value,
    })

    isPaymentConfirmed.value = true
    confirmedOrderId.value = summary.order_id || orderId.value

    // Remove the purchased package from cart session if present.
    try {
      const key = 'gradgownrental_cart_session'
      const raw = localStorage.getItem(key)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (isCartCheckout.value) {
          localStorage.removeItem(key)
        } else {
          const nextItems = Array.isArray(parsed.items)
            ? parsed.items.filter((item) => Number(item.packageId) !== Number(packageId.value))
            : []
          if (nextItems.length) {
            localStorage.setItem(
              key,
              JSON.stringify({
                ...parsed,
                items: nextItems,
              }),
            )
          } else {
            localStorage.removeItem(key)
          }
        }
      }
    } catch {
      // Ignore cart cleanup errors and keep payment success flow.
    }
  } catch (err) {
    paymentError.value = err.message || 'Payment failed. Please retry.'
  } finally {
    isSubmittingPayment.value = false
  }
}

async function initStripeCardElement() {
  if (cardElement) return

  if (!stripePublicKey) {
    stripeError.value = 'Missing VITE_STRIPE_PUBLISHABLE_KEY in frontend env.'
    return
  }

  try {
    await loadStripeJs()
    stripe = window.Stripe(stripePublicKey)
    elements = stripe.elements()
    cardElement = elements.create('card')
    cardElement.mount('#stripe-card-element')
  } catch (err) {
    stripeError.value = err.message || 'Failed to initialize Stripe card input.'
  }
}

function loadStripeJs() {
  return new Promise((resolve, reject) => {
    if (window.Stripe) {
      resolve()
      return
    }
    const existing = document.querySelector('script[src="https://js.stripe.com/v3/"]')
    if (existing) {
      existing.addEventListener('load', resolve, { once: true })
      existing.addEventListener('error', () => reject(new Error('Failed to load Stripe.js')), {
        once: true,
      })
      return
    }
    const script = document.createElement('script')
    script.src = 'https://js.stripe.com/v3/'
    script.async = true
    script.onload = resolve
    script.onerror = () => reject(new Error('Failed to load Stripe.js'))
    document.head.appendChild(script)
  })
}

function toISODate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function getOrdinalSuffix(d) {
  if (d > 3 && d < 21) return 'th'
  switch (d % 10) {
    case 1:
      return 'st'
    case 2:
      return 'nd'
    case 3:
      return 'rd'
    default:
      return 'th'
  }
}

function formatDate(date) {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]
  const dayName = days[date.getDay()]
  const monthName = months[date.getMonth()]
  const day = date.getDate()
  return `${dayName}, ${monthName} ${day}${getOrdinalSuffix(day)}`
}
</script>

<template>
  <div class="order-page pt-5 pb-5">
    <!-- Top-Right Fixed Notification Toast -->
    <div
      v-if="isPaymentConfirmed"
      class="position-fixed top-0 end-0 p-4 slide-in-right"
      style="z-index: 1050; margin-top: 75px"
    >
      <div
        class="bg-light-beige rounded-4 shadow p-4 border"
        style="width: 380px; border-color: rgba(0, 0, 0, 0.05) !important"
      >
        <h5 class="fw-bold text-dark mb-2">Order Confirmed!</h5>
        <p class="text-dark mb-0 lh-base" style="font-size: 0.95rem">
          Order ID: {{ confirmedOrderId || orderId }}. You can now track this order.
        </p>
      </div>
    </div>

    <div class="container fade-in">
      <!-- Top Navigation / Steps -->
      <div class="d-flex justify-content-between align-items-center mb-4 mt-2">
        <button
          @click="goBack"
          class="btn btn-link text-dark text-decoration-none p-0 fw-medium fs-6 d-flex align-items-center gap-2"
        >
          <i class="bi bi-arrow-left"></i>
          {{ backButtonLabel }}
        </button>
        <div class="d-flex align-items-center gap-2">
          <div class="step-dots d-flex gap-2">
            <div class="step-dot" :class="{ active: currentStep >= 1 }"></div>
            <div class="step-dot" :class="{ active: currentStep >= 2 }"></div>
            <div class="step-dot" :class="{ active: currentStep >= 3 }"></div>
            <div class="step-dot" :class="{ active: currentStep >= 4 }"></div>
          </div>
          <span class="ms-2 fw-bold text-secondary small step-text"
            >STEP {{ currentStep }} OF 4</span
          >
        </div>
      </div>

      <div class="row g-5">
        <!-- Left Column: Form -->
        <div class="col-lg-8">
          <div class="bg-white rounded-5 shadow-sm p-5 border-0 position-relative">
            <!-- STEP 1: Configure -->
            <div v-if="currentStep === 1" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Configure Your Rental</h2>
              <p class="text-secondary mb-5">
                Reserve up to 90 days in advance. 3-day standard rental period.
              </p>
              <div v-if="packageLoading" class="alert alert-info mb-4">
                Loading package details...
              </div>
              <div v-if="packageError" class="alert alert-danger mb-4">{{ packageError }}</div>

              <hr class="mb-5 custom-hr" />

              <div class="row g-5 mb-5">
                <!-- Select Size -->
                <div class="col-md-6">
                  <h5 class="fw-bold text-dark mb-4">
                    {{ isCartCheckout ? 'Selected Sizes' : 'Select Size' }}
                  </h5>
                  <div v-if="!isCartCheckout" class="d-flex flex-column gap-4">
                    <div v-for="item in sizeOptions" :key="item.itemType">
                      <p class="text-secondary small fw-bold mb-2 text-uppercase" style="letter-spacing: 1px;">
                        {{ item.itemName }}
                      </p>
                      <div class="d-flex gap-2 flex-wrap">
                        <button
                          v-for="model in item.models"
                          :key="model.modelId"
                          class="btn size-btn fw-bold"
                          :class="selectedSizes[item.itemType] === model.modelId ? 'active' : ''"
                          @click="selectedSizes[item.itemType] = model.modelId"
                        >
                          {{ model.size }}
                        </button>
                      </div>
                    </div>
                  </div>
                  <div v-else class="d-flex flex-column gap-2">
                    <div
                      v-for="item in cartCheckoutItems"
                      :key="item.cartKey || item.packageId"
                      class="bg-light rounded-3 px-3 py-2"
                    >
                      <span class="text-dark fw-medium d-block">{{ item.title }}</span>
                      <span v-for="m in (item.selectedModels || [])" :key="m.modelId" class="fw-bold small me-2">
                        {{ m.itemType }}: {{ m.size }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Fulfillment Method -->
                <div class="col-md-6">
                  <h5 class="fw-bold text-dark mb-4">Fulfillment Method</h5>
                  <div class="d-flex flex-column gap-3">
                    <!-- In-Store Pickup -->
                    <div
                      class="fulfillment-card d-flex align-items-center gap-3 p-3 rounded-4 cursor-pointer"
                      :class="fulfillment === 'pickup' ? 'active' : ''"
                      @click="fulfillment = 'pickup'"
                    >
                      <i
                        class="bi fs-5"
                        :class="
                          fulfillment === 'pickup'
                            ? 'bi-record-circle-fill text-warning-custom'
                            : 'bi-circle text-muted'
                        "
                      ></i>
                      <div
                        class="icon-box-small bg-light-beige rounded-3 d-flex justify-content-center align-items-center"
                      >
                        <i class="bi bi-bag text-warning-custom fs-5"></i>
                      </div>
                      <div>
                        <h6 class="fw-bold mb-0 text-dark">In-Store Pickup</h6>
                        <small class="text-secondary">Free collection at main campus</small>
                      </div>
                    </div>

                    <!-- Home Delivery -->
                    <div
                      class="fulfillment-card d-flex align-items-center gap-3 p-3 rounded-4"
                      :class="[
                        fulfillment === 'delivery' ? 'active' : '',
                        isDeliveryDisabled ? 'disabled' : 'cursor-pointer',
                      ]"
                      @click="!isDeliveryDisabled && (fulfillment = 'delivery')"
                    >
                      <i
                        class="bi fs-5"
                        :class="
                          fulfillment === 'delivery'
                            ? 'bi-record-circle-fill text-warning-custom'
                            : 'bi-circle text-muted'
                        "
                      ></i>
                      <div
                        class="icon-box-small bg-danger-soft rounded-3 d-flex justify-content-center align-items-center"
                        :class="isDeliveryDisabled ? 'opacity-50' : ''"
                      >
                        <i
                          class="bi bi-truck text-danger-custom fs-5"
                          :class="isDeliveryDisabled ? 'opacity-50' : ''"
                        ></i>
                      </div>
                      <div>
                        <h6
                          class="fw-bold mb-0 text-dark"
                          :class="isDeliveryDisabled ? 'opacity-50' : ''"
                        >
                          Home Delivery
                        </h6>
                        <small
                          class="text-secondary"
                          :class="isDeliveryDisabled ? 'opacity-50' : ''"
                        >
                          {{
                            isDeliveryDisabled
                              ? 'Not available for same-day rental'
                              : '$5 flat rate fee'
                          }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <hr class="mb-5 custom-hr" />

              <!-- Select Ceremony Date -->
              <div class="d-flex flex-column align-items-center mb-5">
                <h5 class="fw-bold text-dark mb-4 text-center">Select Your Ceremony Date</h5>

                <div
                  class="calendar-wrapper border rounded-5 p-4 bg-white d-flex flex-column align-items-center"
                  style="width: 320px"
                >
                  <div class="d-flex justify-content-between align-items-center w-100 mb-4 px-2">
                    <!-- Prev Button or placeholder -->
                    <button
                      @click="prevMonth"
                      v-if="canGoPrev"
                      class="btn btn-sm btn-link text-muted shadow-none p-0"
                    >
                      <i class="bi bi-chevron-left fs-6"></i>
                    </button>
                    <div v-else style="width: 16px"></div>

                    <span class="fw-bold text-dark">{{ viewingMonthYear }}</span>

                    <!-- Next Button or placeholder -->
                    <button
                      @click="nextMonth"
                      v-if="canGoNext"
                      class="btn btn-sm btn-link text-dark shadow-none p-0"
                    >
                      <i class="bi bi-chevron-right fs-6"></i>
                    </button>
                    <div v-else style="width: 16px"></div>
                  </div>

                  <div class="calendar-grid w-100">
                    <div class="text-center small text-secondary fw-bold calendar-header">Su</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">Mo</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">Tu</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">We</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">Th</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">Fr</div>
                    <div class="text-center small text-secondary fw-bold calendar-header">Sa</div>

                    <div
                      v-for="(day, idx) in calendarDays"
                      :key="idx"
                      class="calendar-day text-center small fw-medium"
                      :class="{
                        'cursor-pointer': !day.empty && !day.disabled,
                        active:
                          selectedFullDate &&
                          day.fullDate &&
                          selectedFullDate.getTime() === day.fullDate.getTime(),
                        'text-muted-light': day.empty || day.disabled,
                        'text-dark': !day.empty && !day.disabled,
                      }"
                      @click="!day.empty && !day.disabled && (selectedFullDate = day.fullDate)"
                    >
                      {{ day.date || '' }}
                    </div>
                  </div>
                </div>
              </div>

              <hr class="mb-4 custom-hr" />

              <div class="d-flex justify-content-end w-100">
                <button
                  class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom"
                  :disabled="!canProceedStep1"
                  @click="currentStep = 2"
                >
                  Continue <i class="bi bi-arrow-right ms-2"></i>
                </button>
              </div>
            </div>
            <!-- End Step 1 -->

            <!-- STEP 2: Contact Information -->
            <div v-if="currentStep === 2" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Contact Information</h2>
              <p class="text-secondary mb-5">Please provide your details for the order.</p>

              <hr class="mb-5 custom-hr" />

              <div class="row g-4 mb-5">
                <div class="col-md-6">
                  <label class="form-label fw-bold text-dark mb-2">First Name</label>
                  <input
                    type="text"
                    class="form-control form-control-lg bg-light border-0 py-3"
                    placeholder="e.g. John"
                    v-model="contact.firstName"
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold text-dark mb-2">Last Name</label>
                  <input
                    type="text"
                    class="form-control form-control-lg bg-light border-0 py-3"
                    placeholder="e.g. Doe"
                    v-model="contact.lastName"
                  />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-dark mb-2">Email Address</label>
                  <input
                    type="email"
                    class="form-control form-control-lg bg-light border-0 py-3"
                    placeholder="john.doe@example.com"
                    v-model="contact.email"
                  />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-dark mb-2">Phone Number</label>
                  <input
                    type="text"
                    class="form-control form-control-lg bg-light border-0 py-3"
                    placeholder="+65 9123 4567"
                    v-model="contact.phone"
                  />
                </div>
              </div>

              <hr class="mt-5 mb-5 custom-hr" />

              <div class="d-flex justify-content-end w-100 mt-4">
                <button
                  class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom"
                  :disabled="!isContactValid"
                  @click="currentStep = 3"
                >
                  Continue
                </button>
              </div>
            </div>
            <!-- End Step 2 -->

            <!-- STEP 3: Rental Policies -->
            <div v-if="currentStep === 3" class="fade-in">
              <h2 class="fw-bold text-dark mb-5">Rental Policies</h2>

              <div
                class="sanitization-box rounded-5 p-4 px-xl-4 border-warning-soft d-flex align-items-start gap-4 mb-4"
              >
                <i class="bi bi-shield-check text-warning-custom fs-2 mt-1"></i>
                <p class="text-dark fs-5 lh-base mb-0">
                  Standard <span class="fw-bold">3-day rental window.</span> Late returns incur a
                  full $150 security deposit forfeiture. All gowns are professionally sanitized and
                  pressed before handover.
                </p>
              </div>

              <hr class="mt-5 mb-5 custom-hr" />

              <div class="d-flex justify-content-end w-100 mt-4">
                <button
                  class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom shadow-sm d-flex align-items-center gap-2"
                  :disabled="isReviewLoading"
                  @click="goToReview"
                >
                  {{ isReviewLoading ? 'Reserving...' : 'Review Order' }}
                  <i class="bi bi-arrow-right"></i>
                </button>
              </div>
              <div v-if="reviewError" class="alert alert-danger mt-3">{{ reviewError }}</div>
            </div>
            <!-- End Step 3 -->

            <!-- STEP 4: Review & Checkout -->
            <div v-if="currentStep === 4" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Review & Checkout</h2>
              <p class="text-secondary mb-5">
                Final check of your details before processing payment.
              </p>

              <div class="row g-4 mb-4">
                <!-- Left: Reserved Item Box -->
                <div class="col-md-6">
                  <div
                    class="bg-light-beige rounded-5 p-4 h-100 border-0"
                    style="background-color: #fbf7ef"
                  >
                    <div class="d-flex align-items-center gap-3 mb-4 mt-2">
                      <div
                        class="bg-white rounded-circle d-flex justify-content-center align-items-center shadow-sm"
                        style="width: 70px; height: 70px"
                      >
                        <i class="bi bi-mortarboard text-warning-custom fs-2"></i>
                      </div>
                      <div class="pe-2">
                        <span
                          class="text-secondary fw-bold"
                          style="font-size: 0.75rem; letter-spacing: 1px"
                          >RESERVED ITEM</span
                        >
                        <h4 class="fw-bold text-dark mb-0 lh-1 mt-1">{{ packageTitle }}</h4>
                        <p v-if="isCartCheckout" class="text-secondary mb-0 mt-1 small">
                          {{ cartCheckoutItems.length }} packages
                        </p>
                      </div>
                    </div>

                    <div class="d-flex justify-content-between align-items-center mt-5 mb-3">
                      <span class="text-secondary fw-bold fs-6">Size</span>
                      <span
                        class="bg-white px-3 py-1 rounded-pill border fw-bold text-dark small shadow-sm"
                      >
                      <template v-if="isCartCheckout">Mixed (Per Item)</template>
                      <template v-else>
                        <span v-for="item in sizeOptions" :key="item.itemType" class="me-1">
                          {{ item.itemType }}: {{ sizeOptions.find(i=>i.itemType===item.itemType)?.models.find(m=>m.modelId===selectedSizes[item.itemType])?.size || '—' }}
                        </span>
                      </template>
                      </span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <span class="text-secondary fw-bold fs-6">Fulfillment</span>
                      <span class="fw-bold text-dark fs-6">{{ fulfillment.toUpperCase() }}</span>
                    </div>
                    <div v-if="!isCartCheckout" class="mt-4">
                      <span class="text-secondary fw-bold fs-6 d-block mb-2">Included Items</span>
                      <div class="small text-secondary">
                        <div v-for="item in selectedItemSummary" :key="item.key">
                          {{ item.itemName }}<span v-if="item.size"> ({{ item.size }})</span> x {{ item.qty }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right: Billing & Payment -->
                <div class="col-md-6 d-flex flex-column gap-4">
                  <!-- User Details -->
                  <div class="d-flex gap-3 align-items-center mt-3 ms-2">
                    <div
                      class="bg-light-beige rounded-circle d-flex justify-content-center align-items-center"
                      style="width: 55px; height: 55px; background-color: #fbf7ef"
                    >
                      <i class="bi bi-person text-warning-custom fs-3"></i>
                    </div>
                    <div>
                      <span
                        class="text-secondary fw-bold"
                        style="font-size: 0.75rem; letter-spacing: 1px"
                        >BILLING & DELIVERY TO</span
                      >
                      <h4 class="fw-bold text-dark mb-0 mt-1">
                        {{ contact.firstName }} {{ contact.lastName }}
                      </h4>
                      <p class="text-secondary mb-0">{{ contact.email }}</p>
                    </div>
                  </div>

                  <!-- Secure Payment Box -->
                  <div
                    class="mt-auto rounded-5 p-4 pe-5 border"
                    style="
                      border-color: rgba(181, 74, 42, 0.2) !important;
                      background-color: #fffaf8 !important;
                    "
                  >
                    <div class="d-flex align-items-center gap-2 mb-3">
                      <i class="bi bi-credit-card text-danger-custom fs-5"></i>
                      <span
                        class="text-danger-custom fw-bold"
                        style="font-size: 0.75rem; letter-spacing: 1px"
                        >SECURE PAYMENT</span
                      >
                    </div>
                    <div class="mb-3 small text-secondary">
                      Sandbox cards: <code>4242 4242 4242 4242</code> (success),
                      <code>4000 0000 0000 0002</code> (declined), any future expiry/CVC.
                    </div>
                    <div id="stripe-card-element" class="form-control py-3 mb-3"></div>
                    <p class="text-secondary mb-0 lh-base fw-medium" style="font-size: 0.95rem">
                      Your ${{ depositFee.toFixed(2) }} security deposit will be authorized and held
                      until the successful return of the regalia.
                    </p>
                  </div>
                </div>
              </div>

              <hr class="mt-5 mb-4 custom-hr" />

              <button
                class="btn btn-warning text-white fw-bold rounded-pill w-100 py-3 fs-3 shadow-sm mb-3"
                @click="confirmPayment"
                :disabled="isPaymentConfirmed || isSubmittingPayment || !orderId"
              >
                <span v-if="!isPaymentConfirmed && !isSubmittingPayment">Confirm Payment</span>
                <span v-else-if="isSubmittingPayment"
                  >Processing <i class="bi bi-arrow-repeat ms-2 rotate-animation"></i
                ></span>
                <span v-else>Payment Confirmed</span>
              </button>
              <div v-if="stripeError" class="alert alert-danger">{{ stripeError }}</div>
              <div v-if="paymentError" class="alert alert-danger">{{ paymentError }}</div>
              <p class="text-center text-secondary small mb-0 fw-medium" style="font-style: italic">
                By confirming, you agree to our 3-day rental period and terms of service.
              </p>
            </div>
          </div>
        </div>

        <!-- Right Column: Summary -->
        <div class="col-lg-4">
          <div class="sticky-top" style="top: 100px">
            <!-- Order Summary -->
            <div class="bg-white rounded-5 shadow-sm p-4 px-xl-5 mb-4 border-0">
              <h4 class="fw-bold text-dark mb-4 mt-2">Order Summary</h4>
              <hr class="custom-hr mb-4" />

              <div class="d-flex justify-content-between mb-4">
                <span class="text-secondary fw-medium fs-5">Rental Package</span>
                <span class="fw-bold text-dark fs-5">${{ rentalFee.toFixed(2) }}</span>
              </div>

              <div class="d-flex justify-content-between mb-4">
                <span class="text-secondary fw-medium fs-5">Security Deposit</span>
                <span class="fw-bold text-dark fs-5">${{ depositFee.toFixed(2) }}</span>
              </div>

              <div class="d-flex justify-content-between mb-4">
                <span class="text-secondary fw-medium fs-5">Delivery Fee</span>
                <span class="fw-bold text-dark fs-5">${{ deliveryFee.toFixed(2) }}</span>
              </div>

              <hr
                class="custom-hr mb-4 border-dashed"
                style="border-top: 2px dashed #e0e0e0; opacity: 1"
              />

              <div class="d-flex justify-content-between align-items-center mb-4 mt-4">
                <span class="fw-bold text-warning-custom display-6 mb-0">Charge Now</span>
                <span class="fw-bold text-warning-custom display-6 mb-0"
                  >${{ totalCost.toFixed(2) }}</span
                >
              </div>
            </div>

            <!-- Selected Item Card -->
            <div class="sanitization-box rounded-5 p-4 px-xl-5 border-warning-soft mb-4">
              <div class="d-flex align-items-center gap-2 mb-3">
                <i class="bi bi-check-circle text-warning-custom fs-6"></i>
                <span class="text-warning-custom fw-bold small" style="letter-spacing: 1px">
                  {{ isCartCheckout ? 'SELECTED ITEMS' : 'SELECTED ITEM' }}
                </span>
              </div>
              <h4 class="fw-bold text-dark mb-1">{{ packageTitle }}</h4>
              <p class="text-secondary fw-bold small mb-0" v-if="!isCartCheckout">
                {{ packageLevel }} Collection
              </p>
              <div v-if="!isCartCheckout" class="small text-secondary mt-2">
                <div v-for="item in selectedItemSummary" :key="item.key">
                  {{ item.itemName }}<span v-if="item.size"> ({{ item.size }})</span> x {{ item.qty }}
                </div>
              </div>
              <div v-else class="small text-secondary">
                <div
                  v-for="item in cartCheckoutItems"
                  :key="item.cartKey || item.packageId"
                >
                  • {{ item.title }}
                  <span v-for="m in (item.selectedModels || [])" :key="m.modelId" class="ms-1">({{ m.itemType }}: {{ m.size }})</span>
                </div>
              </div>
            </div>

            <!-- Timeline Card -->
            <div
              v-if="selectedFullDate"
              class="bg-white rounded-5 p-4 px-xl-5 mb-4 border border-1 fade-in"
              style="border-color: rgba(216, 166, 28, 0.2) !important"
            >
              <div class="mb-4">
                <span class="text-warning-custom fw-bold small" style="letter-spacing: 1px"
                  >YOUR TIMELINE</span
                >
              </div>

              <div class="mb-3">
                <p
                  class="text-secondary fw-bold mb-1"
                  style="font-size: 0.8rem; letter-spacing: 0.5px; opacity: 0.8"
                >
                  PICKUP
                </p>
                <h5 class="text-dark fw-bold mb-0 lh-base">{{ formattedStartDate }}</h5>
              </div>

              <hr class="custom-hr my-4" />

              <div class="mt-3">
                <p
                  class="text-danger-custom fw-bold mb-1"
                  style="font-size: 0.8rem; letter-spacing: 0.5px"
                >
                  RETURN BY
                </p>
                <h5 class="text-dark fw-bold mb-0 lh-base">{{ formattedEndDate }}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-page {
  background-color: #fbf7ef;
  min-height: 100vh;
}

.fade-in {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #e5cd8d;
}
.step-dot.active {
  background-color: #d8a61c;
}

.step-text {
  letter-spacing: 1px;
}

.custom-hr {
  border-color: rgba(0, 0, 0, 0.08);
}

.size-btn {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  border: 2px solid #e1d8c9;
  background-color: transparent;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.2s;
}

.size-btn:hover {
  border-color: #d8a61c;
}

.size-btn.active {
  border-color: #d8a61c;
  background-color: #fdfaf5;
  color: #d8a61c;
}

.fulfillment-card {
  border: 2px solid #e1d8c9;
  background-color: transparent;
  transition: all 0.2s;
}

.fulfillment-card.active {
  border-color: #d8a61c;
  background-color: #fdfaf5;
}

.fulfillment-card.disabled {
  opacity: 0.6;
  border-color: #e1d8c9;
  background-color: transparent;
  cursor: not-allowed !important;
}

.fulfillment-card.disabled:hover {
  border-color: #e1d8c9;
  background-color: transparent;
}

.icon-box-small {
  width: 48px;
  height: 48px;
  min-width: 48px;
}

.bg-light-beige {
  background-color: #f6efe1 !important;
}

.text-warning-custom {
  color: #d8a61c !important;
}

.bg-danger-soft {
  background-color: rgba(181, 74, 42, 0.1);
}

.text-danger-custom {
  color: #b54a2a !important;
}

.cursor-pointer {
  cursor: pointer;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 15px 5px;
}

.calendar-header {
  margin-bottom: 5px;
}

.calendar-day {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.calendar-day:hover:not(.active):not(.text-muted-light) {
  background-color: #f6efe1;
}

.calendar-day.active {
  background-color: #c5532b;
  color: white !important;
}

.text-muted-light {
  color: #ccc !important;
}

.btn-hover-custom {
  background-color: #d8a61c;
  border-color: #d8a61c;
}

.btn-hover-custom:hover {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-hover-custom:disabled {
  opacity: 0.6;
  background-color: #d8a61c;
  border-color: #d8a61c;
}

.sanitization-box {
  background-color: #f6efe1;
}

.border-warning-soft {
  border: 1px solid rgba(216, 166, 28, 0.3);
}

.bg-warning {
  background-color: #d8a61c !important;
}

.custom-input:focus {
  background-color: #fff !important;
  box-shadow: 0 0 0 0.25rem rgba(216, 166, 28, 0.25);
}

.slide-in-right {
  animation: slideInRight 0.4s ease-out forwards;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.rotate-animation {
  display: inline-block;
  animation: rotation 1.5s infinite linear;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}
</style>
