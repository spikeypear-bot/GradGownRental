<script>
export default {
  name: 'inventory' // needed for keep-alive to work seamlessly
}
</script>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import inventoryService from '@/services/inventory/index.js'

const router = useRouter()
const route = useRoute()
const inventoryApiBase = import.meta.env.VITE_INVENTORY_API_BASE_URL || 'http://localhost:8080/api/inventory'

const selectedLevel = ref('')
const selectedInstitution = ref('')
const selectedFaculty = ref('')

// API Data
const allPackages = ref([])
const institutions = ref([])
const faculties = ref([])
const loading = ref(false)
const error = ref(null)

// Cart/session (10-minute soft reservation window in UI)
const CART_STORAGE_KEY = 'gradgownrental_cart_session'
const SESSION_MS = 10 * 60 * 1000
const cartItems = ref([])
const cartExpiresAt = ref(0)
const cartActive = computed(() => cartExpiresAt.value > Date.now())

function loadCartSession() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    cartExpiresAt.value = Number(parsed.expiresAt || 0)
    cartItems.value = Array.isArray(parsed.items) ? parsed.items : []
    if (cartExpiresAt.value <= Date.now()) {
      clearCartSession()
    }
  } catch {
    clearCartSession()
  }
}

function saveCartSession() {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify({
    expiresAt: cartExpiresAt.value,
    items: cartItems.value
  }))
}

function clearCartSession() {
  cartExpiresAt.value = 0
  cartItems.value = []
  localStorage.removeItem(CART_STORAGE_KEY)
}

function ensureActiveSession() {
  if (!cartActive.value) {
    cartExpiresAt.value = Date.now() + SESSION_MS
    cartItems.value = []
  }
}

function readCartSession() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY)
    if (!raw) return { expiresAt: 0, items: [] }
    const parsed = JSON.parse(raw)
    return {
      expiresAt: Number(parsed.expiresAt || 0),
      items: Array.isArray(parsed.items) ? parsed.items : []
    }
  } catch {
    return { expiresAt: 0, items: [] }
  }
}

function addSelectedToCart() {
  if (!selectedPackage.value) return
  if (!selectedCartSize.value) {
    sizeRequiredError.value = 'Please choose a size before adding to cart.'
    return
  }
  sizeRequiredError.value = ''

  // Always read FRESH cart from localStorage first
  const current = readCartSession()
  const cartKey = `${selectedPackage.value.packageId}:${selectedCartSize.value}`
  const exists = current.items.some(item => item.cartKey === cartKey)

  if (!exists) {
    const newItem = {
      cartKey,
      packageId: selectedPackage.value.packageId,
      title: selectedPackage.value.title,
      price: selectedPackage.value.price,
      rentalFee: selectedPackage.value.rentalFee,
      deposit: selectedPackage.value.deposit,
      educationLevel: selectedPackage.value.educationLevel,
      institution: selectedPackage.value.institution,
      faculty: selectedPackage.value.faculty,
      selectedSize: selectedCartSize.value
    }

    const nextItems = [...current.items, newItem]
    const nextExpiresAt = current.expiresAt && current.expiresAt > Date.now() 
      ? current.expiresAt 
      : Date.now() + 10 * 60 * 1000

    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify({
      expiresAt: nextExpiresAt,
      items: nextItems
    }))

    // Update local state to match
    cartItems.value = nextItems
    cartExpiresAt.value = nextExpiresAt
  }
}

function goToCart() {
  router.push('/cart')
}

function closeDetails() {
  selectedPackage.value = null
  selectedCartSize.value = ''
  sizeRequiredError.value = ''
}

// Fetch packages on component mount
onMounted(async () => {
  loadCartSession()
  if (cartExpiresAt.value > 0 && cartExpiresAt.value <= Date.now()) {
    clearCartSession()
  }

  console.log('🔄 InventoryView mounted - starting API fetch')
  loading.value = true
  error.value = null
  try {
    const packages = await inventoryService.getAllPackages()
    allPackages.value = packages
    console.log('✅ Fetched packages:', packages.length, 'items')
    console.log('📦 Sample package:', packages[0])
    
    // Extract unique institutions and faculties
    const instSet = new Set()
    const facSet = new Set()
    
    allPackages.value.forEach(pkg => {
      if (pkg.institution) instSet.add(pkg.institution)
      if (pkg.faculty) facSet.add(pkg.faculty)
    })
    
    institutions.value = Array.from(instSet).sort()
    faculties.value = Array.from(facSet).sort()
    console.log('✅ Extracted institutions:', institutions.value.length)
    console.log('✅ Extracted faculties:', faculties.value.length)
  } catch (err) {
    error.value = err?.message || 'Failed to load packages from API'
    console.error('❌ Error fetching packages:', err)
    institutions.value = []
    faculties.value = []
  } finally {
    loading.value = false
  }
})

// Extract unique education levels from packages
const educationLevels = computed(() => {
  const levels = new Set()
  allPackages.value.forEach(pkg => {
    if (pkg.educationLevel) levels.add(pkg.educationLevel)
  })
  const result = Array.from(levels).sort()
  console.log('📚 Education levels computed:', result)
  return result
})

// Filter packages based on user selections
const filteredPackages = computed(() => {
  const filtered = allPackages.value.filter(pkg => {
    // Apply filters only if they're selected
    if (selectedLevel.value && pkg.educationLevel !== selectedLevel.value) return false
    if (selectedInstitution.value && pkg.institution !== selectedInstitution.value) return false
    if (selectedFaculty.value && pkg.faculty !== selectedFaculty.value) return false
    return true
  })
  
  console.log('Filter criteria:', {
    level: selectedLevel.value || 'all',
    institution: selectedInstitution.value || 'all',
    faculty: selectedFaculty.value || 'all',
    matchCount: filtered.length,
    totalPackages: allPackages.value.length
  })
  return filtered
})

const selectedPackage = ref(null)
const selectedCartSize = ref('')
const sizeRequiredError = ref('')

function sortSizes(sizes) {
  const sortOrder = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
  return [...new Set(sizes)].sort((a, b) => {
    const ai = sortOrder.indexOf(a)
    const bi = sortOrder.indexOf(b)
    if (ai === -1 && bi === -1) return a.localeCompare(b)
    if (ai === -1) return 1
    if (bi === -1) return -1
    return ai - bi
  })
}

function getCommonSizes(styleBuckets) {
  const styleSizeSets = styleBuckets
    .map(style => new Set((style.models || []).map(m => String(m.size || '').toUpperCase()).filter(Boolean)))
    .filter(set => set.size > 0)

  if (!styleSizeSets.length) return []
  let intersection = styleSizeSets[0]
  for (let i = 1; i < styleSizeSets.length; i++) {
    intersection = new Set([...intersection].filter(size => styleSizeSets[i].has(size)))
  }
  return sortSizes([...intersection])
}

const selectPackage = async (packageObj) => {
  // Build display with all styles
  const styles = packageObj.getStyles()
  const styleNames = styles.map(s => s.itemName).join(' + ')

  let detailedStyleBuckets = []
  try {
    const detail = await inventoryService.getPackageById(packageObj.packageId)
    detailedStyleBuckets = detail.getStyleBuckets()
  } catch (err) {
    console.warn('Falling back to summary package data for sizes:', err)
  }

  const commonSizes = getCommonSizes(detailedStyleBuckets)
  selectedCartSize.value = commonSizes[0] || ''
  sizeRequiredError.value = ''

  selectedPackage.value = {
    packageId: packageObj.packageId,
    title: `${packageObj.institution} - ${packageObj.educationLevel}`,
    subtitle: `${packageObj.faculty}`,
    educationLevel: packageObj.educationLevel,
    institution: packageObj.institution,
    faculty: packageObj.faculty,
    price: packageObj.totalPrice,
    rentalFee: packageObj.totalRentalFee,
    deposit: packageObj.totalDeposit,
    features: styles.map(s => s.itemName),
    shortDesc: 'Premium academic regalia rentals with professional cleaning',
    longDesc: `Complete ${packageObj.educationLevel} regalia package including: ${styleNames}. All items are professionally cleaned and maintained to the highest standards.`,
    styles: styles,
    availableSizes: commonSizes
  }
}

watch(() => route.query.new, (newVal) => {
  if (newVal === 'true') {
    selectedLevel.value = ''
    selectedInstitution.value = ''
    selectedFaculty.value = ''
    selectedPackage.value = null
    selectedCartSize.value = ''
    sizeRequiredError.value = ''
    // Clean up url directly to prevent refresh-stickiness
    router.replace({ path: '/inventory' })
  }
}, { immediate: true })

</script>

<template>
  <div class="inventory-page pt-5">
    <!-- Package Details Overlay Screen -->
    <div v-if="selectedPackage" class="container py-4 fade-in">
      <button @click="closeDetails" class="btn btn-link text-dark text-decoration-none p-0 mb-4 fw-medium fs-5">
        <i class="bi bi-arrow-left me-2"></i> Back to Collections
      </button>
      
      <div class="row g-5">
        <!-- Left Column: Image Card -->
        <div class="col-lg-5 position-relative">
          <div class="sticky-top" style="top: 100px;">
            <div class="card border-0 rounded-4 shadow-sm bg-white d-flex flex-column align-items-center justify-content-center p-5 position-relative" style="height: 500px;">
              <span class="badge bg-warning text-white rounded-pill px-4 py-2 position-absolute top-0 start-0 m-4 fw-bold mt-4 ms-4 shadow-sm" style="letter-spacing: 1px;">
                {{ selectedPackage.subtitle.toUpperCase() }} COLLECTION
              </span>
              <div class="icon-box-large bg-light-beige rounded-4 d-flex justify-content-center align-items-center mb-4 mt-5">
                <i class="bi bi-mortarboard fs-1 text-warning-custom"></i>
              </div>
              <h3 class="fw-bold text-dark mt-3 mb-1">{{ selectedPackage.title }}</h3>
              <p class="text-secondary fw-bold small" style="letter-spacing: 2px;">{{ selectedPackage.subtitle }}</p>
            </div>
            
            <!-- Thumbnails -->
            <div class="d-flex gap-3 mt-3 justify-content-between">
              <div v-for="i in 3" :key="i" class="bg-white rounded-4 shadow-sm d-flex justify-content-center align-items-center flex-fill" style="height: 100px;">
                <i class="bi bi-box-seam fs-3 text-warning-muted opacity-50"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Details -->
        <div class="col-lg-7 px-lg-4 text-start">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <h1 class="fw-bold display-4 text-dark mb-0">{{ selectedPackage.title }}</h1>
            <div class="text-end">
              <h1 class="fw-bold text-danger-custom mb-0">${{ selectedPackage.price }}</h1>
              <p class="text-secondary small fw-bold mb-0 lh-1" style="letter-spacing: 1px;">PER 3-DAY<br>RENTAL</p>
            </div>
          </div>
          
          <p class="text-secondary fs-5 mb-5">{{ selectedPackage.shortDesc }}</p>
          
          <!-- Premium Features -->
          <div class="d-flex align-items-center gap-2 mb-4">
            <i class="bi bi-check-circle text-warning-custom fs-4"></i>
            <h4 class="fw-bold mb-0 text-dark">Premium Features</h4>
          </div>
          
          <div class="d-flex flex-column gap-3 mb-5">
            <div v-for="(feature, idx) in selectedPackage.features" :key="'f-'+idx" class="bg-white rounded-3 shadow-sm p-4 d-flex align-items-center gap-3">
              <div class="feature-dot bg-warning rounded-circle"></div>
              <span class="fw-bold text-dark">{{ feature }}</span>
            </div>
          </div>
          
          <!-- About the Collection -->
          <h4 class="fw-bold text-dark mb-3">About the Collection</h4>
          <p class="text-secondary mb-4">{{ selectedPackage.longDesc }}</p>
          
          <div class="sanitization-box rounded-4 p-4 d-flex gap-3 align-items-start mb-5 border-danger-soft">
            <i class="bi bi-shield-check text-danger-custom fs-4"></i>
            <div>
              <h6 class="fw-bold text-danger-custom mb-2">Sanitization Standard</h6>
              <p class="text-secondary small mb-0">
                All collections undergo medical-grade steam cleaning and professional pressing between every rental. We enforce a 4-day gap for every item to ensure the highest standards of hygiene and presentation.
              </p>
            </div>
          </div>
          
          <div class="mb-4">
            <h5 class="fw-bold text-dark mb-3">Select Size</h5>
            <div v-if="selectedPackage.availableSizes?.length" class="d-flex gap-2 flex-wrap">
              <button
                v-for="size in selectedPackage.availableSizes"
                :key="size"
                class="btn btn-outline-dark rounded-pill fw-bold px-3 py-2"
                :class="{ active: selectedCartSize === size }"
                @click="selectedCartSize = size"
              >
                {{ size }}
              </button>
            </div>
            <div v-else class="text-secondary small">
              Unable to load available sizes for this package.
            </div>
          </div>

          <hr class="mb-4 d-none d-lg-block border-0 opacity-0">
          
          <button @click="addSelectedToCart" class="btn btn-warning text-white fw-bold rounded-4 py-3 fs-5 w-100 btn-hover-custom mb-3">
            Add To Cart <i class="bi bi-cart-plus ms-2"></i>
          </button>
          <button @click="goToCart" class="btn btn-outline-dark fw-bold rounded-4 py-2 fs-6 w-100 mb-3">
            View Cart <i class="bi bi-arrow-right ms-1"></i>
          </button>
          <div v-if="sizeRequiredError" class="alert alert-danger py-2 mb-3 small">{{ sizeRequiredError }}</div>
          <div class="d-flex gap-2 text-secondary align-items-center justify-content-center">
            <i class="bi bi-info-circle small"></i>
            <span class="small fw-bold" style="letter-spacing: 1px;">SELECT SIZE AND RENTAL DATE DURING CHECKOUT.</span>
          </div>
        </div>
      </div>
    </div>


    <div v-else class="container text-center py-4 fade-in">
      <h1 class="fw-bold display-4 mb-3 text-dark mt-2">Start Your Gown Rental</h1>
      <p class="text-secondary fs-5 mb-5">Please follow the selection flow to find the correct regalia for your ceremony.</p>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-danger alert-dismissible fade show mb-4" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <strong>{{ error }}</strong>
        <p class="small mb-0 mt-2">Please ensure the backend API is running at {{ inventoryApiBase }}</p>
      </div>

      <!-- Loading Message -->
      <div v-if="loading" class="alert alert-info mb-4">
        <i class="bi bi-hourglass-split me-2"></i>
        Loading packages...
      </div>

      <!-- Selection Steps -->
      <div class="row g-4 justify-content-center mb-5 max-w-1000 mx-auto">
        <!-- Step 1 -->
        <div class="col-md-4">
          <div class="card bg-white border-0 shadow-sm h-100 rounded-4 text-start p-4">
            <div class="d-flex align-items-center gap-2 mb-3 text-warning fw-bold">
              <i class="bi bi-book"></i>
              <span>STEP 1</span>
            </div>
            <label class="form-label text-secondary mb-2 fs-6">Education Level</label>
            <select v-model="selectedLevel" class="form-select custom-select rounded-pill border-0 shadow-none bg-light-beige w-100 px-3 py-2 text-dark">
              <option value="" disabled>Select Level</option>
              <option v-for="level in educationLevels" :key="level" :value="level">{{ level }}</option>
            </select>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="col-md-4">
          <div class="card bg-white border-0 shadow-sm h-100 rounded-4 text-start p-4">
            <div class="d-flex align-items-center gap-2 mb-3 text-warning fw-bold">
              <i class="bi bi-building"></i>
              <span>STEP 2</span>
            </div>
            <label class="form-label mb-2 fs-6 text-secondary">Institution</label>
            <select v-model="selectedInstitution" class="form-select custom-select rounded-pill border-0 shadow-none w-100 px-3 py-2 bg-light-beige text-dark">
              <option value="">Select Institution</option>
              <option v-for="inst in institutions" :key="inst" :value="inst">{{ inst }}</option>
            </select>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="col-md-4">
          <div class="card bg-white border-0 shadow-sm h-100 rounded-4 text-start p-4">
            <div class="d-flex align-items-center gap-2 mb-3 text-warning fw-bold">
              <i class="bi bi-briefcase"></i>
              <span>STEP 3</span>
            </div>
            <label class="form-label mb-2 fs-6 text-secondary">Faculty</label>
            <select v-model="selectedFaculty" class="form-select custom-select rounded-pill border-0 shadow-none w-100 px-3 py-2 bg-light-beige text-dark">
              <option value="">Select Faculty</option>
              <option v-for="faculty in faculties" :key="faculty" :value="faculty">{{ faculty }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Results Section -->
      <div class="results-section fade-in">
        <h2 class="fw-bold text-dark mb-5 text-center">Available Packages</h2>
        
        <div v-if="filteredPackages.length === 0" class="empty-state-box d-flex flex-column align-items-center justify-content-center mx-auto rounded-5 border-dashed">
          <i class="bi bi-inbox empty-icon mb-3"></i>
          <h5 class="fw-bold text-secondary">No packages match your filters</h5>
        </div>

        <div v-else class="row g-4 justify-content-center mx-auto">
          
          <!-- Dynamic Package Cards -->
          <div v-for="pkg in filteredPackages" :key="pkg.packageId" class="col-md-6 col-lg-4">
            <div class="card package-card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
              <div class="card-header bg-light-beige border-0 position-relative d-flex justify-content-center align-items-center p-5">
                <span class="price-tag badge bg-warning text-white rounded-pill px-3 py-2 fs-6 fw-bold position-absolute top-0 end-0 mt-3 me-3">${{ pkg.totalPrice }}</span>
                <div class="icon-box bg-white rounded-4 shadow-sm d-flex justify-content-center align-items-center">
                  <i class="bi bi-mortarboard fs-1 text-warning-custom"></i>
                </div>
              </div>
              <div class="card-body p-4 text-start d-flex flex-column">
                <h4 class="fw-bold mb-1 text-dark">{{ pkg.institution }} - {{ pkg.educationLevel }}</h4>
                <p class="text-secondary small mb-3">{{ pkg.faculty }}</p>
                <p class="text-muted small mb-4">Premium academic regalia rentals with professional cleaning</p>
                
                <ul class="list-unstyled mb-5 d-flex flex-column gap-3">
                  <li v-for="(style, idx) in pkg.getStyles()" :key="'pkg-'+pkg.packageId+'-'+idx" class="d-flex align-items-start gap-2">
                    <i class="bi bi-check-circle text-warning-custom mt-1"></i>
                    <span class="text-secondary fs-6">{{ style.itemName }}</span>
                  </li>
                </ul>
                
                <button @click="selectPackage(pkg)" class="btn btn-warning text-white fw-bold rounded-3 py-3 mt-auto fs-6 w-100 btn-hover-custom">
                  View Details <i class="bi bi-arrow-right ms-1"></i>
                </button>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.inventory-page {
  background-color: #fbf7ef;
  min-height: 100vh;
  padding-bottom: 5rem;
}

.max-w-1000 {
  max-width: 1000px;
}

.text-warning {
  color: #d8a61c !important;
}

.text-warning-muted {
  color: #e5cd8d !important; /* Lighter version for inactive steps */
}

.bg-light-beige {
  background-color: #f6efe1 !important;
}

.bg-light-beige-muted {
  background-color: #fdfaf5 !important;
}

.custom-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23888' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 16px 12px;
  cursor: pointer;
}

.custom-select:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.step-inactive {
  opacity: 0.6;
}

.empty-state-box {
  max-width: 1000px;
  min-height: 300px;
  border: 2px dashed #e1d8c9;
  background: transparent;
}

.empty-icon {
  font-size: 4rem;
  color: #cfc4b6;
}

h5 {
  color: #7d7367 !important;
}

.fade-in {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.package-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.package-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08) !important;
}

.icon-box {
  width: 100px;
  height: 100px;
}

.text-warning-custom {
  color: #d8a61c !important;
}

.btn-hover-custom {
  background-color: #d8a61c;
  border-color: #d8a61c;
}

.btn-hover-custom:hover {
  background-color: #c49416;
  border-color: #c49416;
}

.bg-warning {
  background-color: #d8a61c !important;
}

.icon-box-large {
  width: 140px;
  height: 140px;
}

.text-danger-custom {
  color: #b54a2a !important; /* Matches the $65 price and shield icon */
}

.border-danger-soft {
  border: 1px solid rgba(181, 74, 42, 0.2);
}

.sanitization-box {
  background-color: #f6efe1; /* Light beige matching the image */
}

.feature-dot {
  width: 8px;
  height: 8px;
  min-width: 8px;
}

hr {
  border-color: rgba(0,0,0,0.1);
}

/* 3-column layout for package cards */
.col-lg-4 {
  max-width: 33.333333%;
  flex: 0 0 33.333333%;
}

@media (max-width: 1199px) {
  .col-lg-4 {
    max-width: 50%;
    flex: 0 0 50%;
  }
}

@media (max-width: 767px) {
  .col-lg-4,
  .col-md-6 {
    max-width: 100%;
    flex: 0 0 100%;
  }
}
</style>
