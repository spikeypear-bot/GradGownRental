<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const selectedSize = ref('')
const fulfillment = ref('pickup')
const selectedDate = ref(15) // mock default for March 15

// Pull state from query params with fallbacks
const packageTitle = computed(() => route.query.title || 'Bachelors Essential')
const packageLevel = computed(() => route.query.level || 'Bachelors')
const rentalFee = computed(() => Number(route.query.price || 45.00))
const depositFee = 150.00

const totalCost = computed(() => rentalFee.value + depositFee)

const currentStep = ref(1)

const isPaymentConfirmed = ref(false)
const mockOrderId = "GG-VPRQNUI63"

const confirmPayment = () => {
  isPaymentConfirmed.value = true
  setTimeout(() => {
    router.push('/')
  }, 3000) // Redirect after 3 seconds
}

const contact = ref({
  firstName: '',
  lastName: '',
  email: ''
})

const isContactValid = computed(() => {
  return contact.value.firstName.trim() !== '' && 
         contact.value.lastName.trim() !== '' && 
         /^\S+@\S+\.\S+$/.test(contact.value.email)
})

// Calendar & Date Picker Logic
const today = new Date()
const todayNoTime = new Date(today.getFullYear(), today.getMonth(), today.getDate())
const maxDate = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000)

// Also freeze maxDate at midnight to stop any potential time-mismatches in comparison
maxDate.setHours(0,0,0,0)

const viewDate = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const selectedFullDate = ref(null)

const getOrdinalSuffix = (d) => {
  if (d > 3 && d < 21) return 'th'
  switch (d % 10) {
    case 1:  return "st"
    case 2:  return "nd"
    case 3:  return "rd"
    default: return "th"
  }
}

const formatDate = (date) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  
  const dayName = days[date.getDay()]
  const monthName = months[date.getMonth()]
  const day = date.getDate()
  
  return `${dayName}, ${monthName} ${day}${getOrdinalSuffix(day)}`
}

const formattedStartDate = computed(() => {
  if (!selectedFullDate.value) return ''
  return formatDate(selectedFullDate.value)
})

const formattedEndDate = computed(() => {
  if (!selectedFullDate.value) return ''
  const end = new Date(selectedFullDate.value)
  end.setDate(end.getDate() + 2)
  return formatDate(end)
})

const canGoPrev = computed(() => {
  return viewDate.value > new Date(today.getFullYear(), today.getMonth(), 1)
})

const canGoNext = computed(() => {
  const currentViewYear = viewDate.value.getFullYear()
  const currentViewMonth = viewDate.value.getMonth()
  
  const maxYear = maxDate.getFullYear()
  const maxMonth = maxDate.getMonth()
  
  // Only allow next month if our current view is genuinely before the limit
  if (currentViewYear < maxYear) return true
  if (currentViewYear === maxYear && currentViewMonth < maxMonth) return true
  
  return false
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

const viewingMonthYear = computed(() => {
  return viewDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const year = viewDate.value.getFullYear()
  const month = viewDate.value.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()
  
  const days = []
  // Padding for start of month
  for(let i = 0; i < firstDay; i++) {
    days.push({ empty: true })
  }
  // Actual days
  for(let i = 1; i <= daysInMonth; i++) {
    const thisDate = new Date(year, month, i)
    const isDisabled = thisDate < todayNoTime || thisDate > maxDate
    days.push({
      empty: false,
      date: i,
      fullDate: thisDate,
      disabled: isDisabled
    })
  }
  return days
})

const goBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.back()
  }
}
</script>

<template>
  <div class="order-page pt-5 pb-5">
    
    <!-- Top-Right Fixed Notification Toast -->
    <div v-if="isPaymentConfirmed" class="position-fixed top-0 end-0 p-4 slide-in-right" style="z-index: 1050; margin-top: 75px;">
      <div class="bg-light-beige rounded-4 shadow p-4 border" style="width: 380px; border-color: rgba(0,0,0,0.05) !important;">
         <h5 class="fw-bold text-dark mb-2">Order Confirmed!</h5>
         <p class="text-dark mb-0 lh-base" style="font-size: 0.95rem;">Order ID: {{ mockOrderId }}. Redirecting to tracking...</p>
      </div>
    </div>

    <div class="container fade-in">
      
      <!-- Top Navigation / Steps -->
      <div class="d-flex justify-content-between align-items-center mb-4 mt-2">
        <button @click="goBack" class="btn btn-link text-dark text-decoration-none p-0 fw-medium fs-6 d-flex align-items-center gap-2">
          <i class="bi bi-arrow-left"></i> {{ currentStep === 1 ? 'Back to Details' : 'Back to Configuration' }}
        </button>
        <div class="d-flex align-items-center gap-2">
          <div class="step-dots d-flex gap-2">
            <div class="step-dot" :class="{ 'active': currentStep >= 1 }"></div>
            <div class="step-dot" :class="{ 'active': currentStep >= 2 }"></div>
            <div class="step-dot" :class="{ 'active': currentStep >= 3 }"></div>
            <div class="step-dot" :class="{ 'active': currentStep >= 4 }"></div>
          </div>
          <span class="ms-2 fw-bold text-secondary small step-text">STEP {{ currentStep }} OF 4</span>
        </div>
      </div>

      <div class="row g-5">
        <!-- Left Column: Form -->
        <div class="col-lg-8">
          <div class="bg-white rounded-5 shadow-sm p-5 border-0 position-relative">
            
            <!-- STEP 1: Configure -->
            <div v-if="currentStep === 1" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Configure Your Rental</h2>
              <p class="text-secondary mb-5">Reserve up to 90 days in advance. 3-day standard rental period.</p>

              <hr class="mb-5 custom-hr">

              <div class="row g-5 mb-5">
              <!-- Select Size -->
              <div class="col-md-6">
                <h5 class="fw-bold text-dark mb-4">Select Size</h5>
                <div class="d-flex gap-3 flex-wrap">
                  <button v-for="size in ['S', 'M', 'L', 'XL']" :key="size" 
                          class="btn size-btn fw-bold" 
                          :class="selectedSize === size ? 'active' : ''"
                          @click="selectedSize = size">
                    {{ size }}
                  </button>
                </div>
              </div>

              <!-- Fulfillment Method -->
              <div class="col-md-6">
                <h5 class="fw-bold text-dark mb-4">Fulfillment Method</h5>
                <div class="d-flex flex-column gap-3">
                  <!-- In-Store Pickup -->
                  <div class="fulfillment-card d-flex align-items-center gap-3 p-3 rounded-4 cursor-pointer"
                       :class="fulfillment === 'pickup' ? 'active' : ''"
                       @click="fulfillment = 'pickup'">
                    <i class="bi fs-5" :class="fulfillment === 'pickup' ? 'bi-record-circle-fill text-warning-custom' : 'bi-circle text-muted'"></i>
                    <div class="icon-box-small bg-light-beige rounded-3 d-flex justify-content-center align-items-center">
                      <i class="bi bi-bag text-warning-custom fs-5"></i>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-0 text-dark">In-Store Pickup</h6>
                      <small class="text-secondary">Free collection at main campus</small>
                    </div>
                  </div>

                  <!-- Home Delivery -->
                  <div class="fulfillment-card d-flex align-items-center gap-3 p-3 rounded-4 cursor-pointer"
                       :class="fulfillment === 'delivery' ? 'active' : ''"
                       @click="fulfillment = 'delivery'">
                    <i class="bi fs-5" :class="fulfillment === 'delivery' ? 'bi-record-circle-fill text-warning-custom' : 'bi-circle text-muted'"></i>
                    <div class="icon-box-small bg-danger-soft rounded-3 d-flex justify-content-center align-items-center">
                      <i class="bi bi-truck text-danger-custom fs-5"></i>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-0 text-dark">Home Delivery</h6>
                      <small class="text-secondary">$5 flat rate fee</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <hr class="mb-5 custom-hr">

            <!-- Select Ceremony Date -->
            <div class="d-flex flex-column align-items-center mb-5">
              <h5 class="fw-bold text-dark mb-4 text-center">Select Your Ceremony Date</h5>
              
              <div class="calendar-wrapper border rounded-5 p-4 bg-white d-flex flex-column align-items-center" style="width: 320px;">
                <div class="d-flex justify-content-between align-items-center w-100 mb-4 px-2">
                  <!-- Prev Button or placeholder -->
                  <button @click="prevMonth" v-if="canGoPrev" class="btn btn-sm btn-link text-muted shadow-none p-0">
                    <i class="bi bi-chevron-left fs-6"></i>
                  </button>
                  <div v-else style="width: 16px;"></div>
                  
                  <span class="fw-bold text-dark">{{ viewingMonthYear }}</span>
                  
                  <!-- Next Button or placeholder -->
                  <button @click="nextMonth" v-if="canGoNext" class="btn btn-sm btn-link text-dark shadow-none p-0">
                    <i class="bi bi-chevron-right fs-6"></i>
                  </button>
                  <div v-else style="width: 16px;"></div>
                </div>
                
                <div class="calendar-grid w-100">
                  <div class="text-center small text-secondary fw-bold calendar-header">Su</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">Mo</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">Tu</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">We</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">Th</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">Fr</div>
                  <div class="text-center small text-secondary fw-bold calendar-header">Sa</div>
                  
                  <div v-for="(day, idx) in calendarDays" :key="idx" 
                       class="calendar-day text-center small fw-medium"
                       :class="{
                          'cursor-pointer': !day.empty && !day.disabled,
                          'active': selectedFullDate && day.fullDate && selectedFullDate.getTime() === day.fullDate.getTime(),
                          'text-muted-light': day.empty || day.disabled,
                          'text-dark': !day.empty && !day.disabled
                       }"
                       @click="!day.empty && !day.disabled && (selectedFullDate = day.fullDate)">
                    {{ day.date || '' }}
                  </div>
                </div>
              </div>
            </div>

            <hr class="mb-4 custom-hr">
            
            <div class="d-flex justify-content-end w-100">
              <button class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom" :disabled="!selectedSize || !selectedFullDate" @click="currentStep = 2">
                Continue <i class="bi bi-arrow-right ms-2"></i>
              </button>
            </div>
            </div> <!-- End Step 1 -->

            <!-- STEP 2: Contact Information -->
            <div v-if="currentStep === 2" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Contact Information</h2>
              <p class="text-secondary mb-5">Please provide your details for the order.</p>

              <hr class="mb-5 custom-hr">
              
              <div class="row g-4 mb-5">
                <div class="col-md-6">
                  <label class="form-label fw-bold text-dark mb-2">First Name</label>
                  <input type="text" class="form-control form-control-lg bg-light border-0 py-3" placeholder="e.g. John" v-model="contact.firstName">
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold text-dark mb-2">Last Name</label>
                  <input type="text" class="form-control form-control-lg bg-light border-0 py-3" placeholder="e.g. Doe" v-model="contact.lastName">
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-dark mb-2">Email Address</label>
                  <input type="email" class="form-control form-control-lg bg-light border-0 py-3" placeholder="john.doe@example.com" v-model="contact.email">
                </div>
              </div>

              <hr class="mt-5 mb-5 custom-hr">

              <div class="d-flex justify-content-end w-100 mt-4">
                <button 
                  class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom" 
                  :disabled="!isContactValid"
                  @click="currentStep = 3"
                >
                  Continue
                </button>
              </div>
            </div> <!-- End Step 2 -->

            <!-- STEP 3: Rental Policies -->
            <div v-if="currentStep === 3" class="fade-in">
              <h2 class="fw-bold text-dark mb-5">Rental Policies</h2>

              <div class="sanitization-box rounded-5 p-4 px-xl-4 border-warning-soft d-flex align-items-start gap-4 mb-4">
                <i class="bi bi-shield-check text-warning-custom fs-2 mt-1"></i>
                <p class="text-dark fs-5 lh-base mb-0">
                  Standard <span class="fw-bold">3-day rental window.</span> Late returns incur a full $150 security deposit forfeiture. All gowns are professionally sanitized and pressed before handover.
                </p>
              </div>

              <hr class="mt-5 mb-5 custom-hr">

              <div class="d-flex justify-content-end w-100 mt-4">
                <button 
                  class="btn btn-warning text-white fw-bold rounded-pill px-5 py-3 fs-5 btn-hover-custom shadow-sm d-flex align-items-center gap-2" 
                  @click="currentStep = 4"
                >
                  Review Order <i class="bi bi-arrow-right"></i>
                </button>
              </div>
            </div> <!-- End Step 3 -->

            <!-- STEP 4: Review & Checkout -->
            <div v-if="currentStep === 4" class="fade-in">
              <h2 class="fw-bold text-dark mb-1">Review & Checkout</h2>
              <p class="text-secondary mb-5">Final check of your details before processing payment.</p>

              <div class="row g-4 mb-4">
                <!-- Left: Reserved Item Box -->
                <div class="col-md-6">
                  <div class="bg-light-beige rounded-5 p-4 h-100 border-0" style="background-color: #fbf7ef;">
                    <div class="d-flex align-items-center gap-3 mb-4 mt-2">
                      <div class="bg-white rounded-circle d-flex justify-content-center align-items-center shadow-sm" style="width: 70px; height: 70px;">
                         <i class="bi bi-mortarboard text-warning-custom fs-2"></i>
                      </div>
                      <div class="pe-2">
                        <span class="text-secondary fw-bold" style="font-size: 0.75rem; letter-spacing: 1px;">RESERVED ITEM</span>
                        <h4 class="fw-bold text-dark mb-0 lh-1 mt-1">{{ packageTitle }}</h4>
                      </div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mt-5 mb-3">
                       <span class="text-secondary fw-bold fs-6">Size</span>
                       <span class="bg-white px-3 py-1 rounded-pill border fw-bold text-dark small shadow-sm">Standard {{ selectedSize }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                       <span class="text-secondary fw-bold fs-6">Fulfillment</span>
                       <span class="fw-bold text-dark fs-6">{{ fulfillment.toUpperCase() }}</span>
                    </div>
                  </div>
                </div>

                <!-- Right: Billing & Payment -->
                <div class="col-md-6 d-flex flex-column gap-4">
                  <!-- User Details -->
                  <div class="d-flex gap-3 align-items-center mt-3 ms-2">
                    <div class="bg-light-beige rounded-circle d-flex justify-content-center align-items-center" style="width: 55px; height: 55px; background-color: #fbf7ef;">
                      <i class="bi bi-person text-warning-custom fs-3"></i>
                    </div>
                    <div>
                      <span class="text-secondary fw-bold" style="font-size: 0.75rem; letter-spacing: 1px;">BILLING & DELIVERY TO</span>
                      <h4 class="fw-bold text-dark mb-0 mt-1">{{ contact.firstName }} {{ contact.lastName }}</h4>
                      <p class="text-secondary mb-0">{{ contact.email }}</p>
                    </div>
                  </div>

                  <!-- Secure Payment Box -->
                  <div class="mt-auto rounded-5 p-4 pe-5 border" style="border-color: rgba(181, 74, 42, 0.2) !important; background-color: #fffaf8 !important;">
                    <div class="d-flex align-items-center gap-2 mb-3">
                      <i class="bi bi-credit-card text-danger-custom fs-5"></i>
                      <span class="text-danger-custom fw-bold" style="font-size: 0.75rem; letter-spacing: 1px;">SECURE PAYMENT</span>
                    </div>
                    <p class="text-secondary mb-0 lh-base fw-medium" style="font-size: 0.95rem;">
                       Your ${{ depositFee }} security deposit will be authorized and held until the successful return of the regalia.
                    </p>
                  </div>
                </div>
              </div>

              <hr class="mt-5 mb-4 custom-hr">

              <button class="btn btn-warning text-white fw-bold rounded-pill w-100 py-3 fs-3 shadow-sm mb-3" @click="confirmPayment" :disabled="isPaymentConfirmed">
                <span v-if="!isPaymentConfirmed">Confirm Payment</span>
                <span v-else>Processing <i class="bi bi-arrow-repeat ms-2 rotate-animation"></i></span>
              </button>
              <p class="text-center text-secondary small mb-0 fw-medium" style="font-style: italic;">
                By confirming, you agree to our 3-day rental period and terms of service.
              </p>
            </div>
          </div>
        </div>

        <!-- Right Column: Summary -->
        <div class="col-lg-4">
          <div class="sticky-top" style="top: 100px;">
            <!-- Order Summary -->
            <div class="bg-white rounded-5 shadow-sm p-4 px-xl-5 mb-4 border-0">
              <h4 class="fw-bold text-dark mb-4 mt-2">Order Summary</h4>
              <hr class="custom-hr mb-4">
              
              <div class="d-flex justify-content-between mb-4">
                <span class="text-secondary fw-medium fs-5">Rental Package</span>
                <span class="fw-bold text-dark fs-5">${{ rentalFee.toFixed(2) }}</span>
              </div>
              
              <div class="d-flex justify-content-between mb-4">
                <span class="text-secondary fw-medium fs-5">Security Deposit</span>
                <span class="fw-bold text-dark fs-5">${{ depositFee.toFixed(2) }}</span>
              </div>

              <hr class="custom-hr mb-4 border-dashed" style="border-top: 2px dashed #e0e0e0; opacity: 1;">

              <div class="d-flex justify-content-between align-items-center mb-4 mt-4">
                <span class="fw-bold text-warning-custom display-6 mb-0">Total</span>
                <span class="fw-bold text-warning-custom display-6 mb-0">${{ totalCost.toFixed(2) }}</span>
              </div>
            </div>

            <!-- Selected Item Card -->
            <div class="sanitization-box rounded-5 p-4 px-xl-5 border-warning-soft mb-4">
              <div class="d-flex align-items-center gap-2 mb-3">
                <i class="bi bi-check-circle text-warning-custom fs-6"></i>
                <span class="text-warning-custom fw-bold small" style="letter-spacing: 1px;">SELECTED ITEM</span>
              </div>
              <h4 class="fw-bold text-dark mb-1">{{ packageTitle }}</h4>
              <p class="text-secondary fw-bold small mb-0">{{ packageLevel }} Collection</p>
            </div>

            <!-- Timeline Card -->
            <div v-if="selectedFullDate" class="bg-white rounded-5 p-4 px-xl-5 mb-4 border border-1 fade-in" style="border-color: rgba(216, 166, 28, 0.2) !important;">
              <div class="mb-4">
                <span class="text-warning-custom fw-bold small" style="letter-spacing: 1px;">YOUR TIMELINE</span>
              </div>
              
              <div class="mb-3">
                <p class="text-secondary fw-bold mb-1" style="font-size: 0.8rem; letter-spacing: 0.5px; opacity: 0.8;">PICKUP</p>
                <h5 class="text-dark fw-bold mb-0 lh-base">{{ formattedStartDate }}</h5>
              </div>

              <hr class="custom-hr my-4">

              <div class="mt-3">
                <p class="text-danger-custom fw-bold mb-1" style="font-size: 0.8rem; letter-spacing: 0.5px;">RETURN BY</p>
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
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
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
  border-color: rgba(0,0,0,0.08);
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
  from { transform: rotate(0deg); }
  to { transform: rotate(359deg); }
}
</style>