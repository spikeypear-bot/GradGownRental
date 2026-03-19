<script>
export default {
  name: 'inventory' // needed for keep-alive to work seamlessly
}
</script>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const selectedLevel = ref('')
const selectedInstitution = ref('')
const selectedFaculty = ref('')

const institutions = [
  "NUS", "NTU", "SUTD", "SUSS", "ITE", 
  "SINGAPORE POLYTECHNIC", "NGEE ANN POLYTECHNIC", "SMU"
]

const faculties = [
  "Arts", 
  "Applied Science", 
  "Business Administration", 
  "Computing", 
  "Engineering", 
  "Laws", 
  "Medicine and Surgery", 
  "Science",
  "Social Science",
  "All Faculties"
]

const isStep2Enabled = computed(() => selectedLevel.value !== '')
const isStep3Enabled = computed(() => selectedInstitution.value !== '')
const showResults = computed(() => selectedLevel.value !== '' && selectedInstitution.value !== '' && selectedFaculty.value !== '')

const formattedLevel = computed(() => {
  if (selectedLevel.value === 'bachelor') return "Bachelor's"
  if (selectedLevel.value === 'master') return "Master's"
  if (selectedLevel.value === 'phd') return "PhD"
  return ""
})

const getPackageFeatures = (type) => {
  let hood = "Standard satin-lined hood"
  let gown = "Traditional oblong sleeve gown"
  let hat = "Reinforced classic mortarboard"
  
  // Minimal mock logic referring to gay.py
  if (selectedInstitution.value === 'NTU') {
    gown = "Blue Gown with Sleeves"
    if (selectedFaculty.value === "Engineering" && selectedLevel.value === 'bachelor') gown = "Gown with Gold Front"
    if (selectedLevel.value === 'phd') gown = "Gown with Crimson Front and Sleeves"
    
    hood = "Gold edged with White Hood"
    if (selectedLevel.value === 'phd') hood = "Crimson edged with Gold Hood"
    if (selectedFaculty.value === "Arts") hood = "Alizarin Crimson edged with White and Magenta Hood"
    
    hat = selectedLevel.value === 'phd' ? "Bonnet" : "Mortarboard"
  } else if (selectedInstitution.value === 'SMU') {
    gown = "Black Gown with Pointed Sleeves"
    if (selectedLevel.value === 'master') gown = "Black Gown with Oblong Sleeves"
    if (selectedLevel.value === 'phd') gown = "Black Gown with Yellow Front and Sides"
    
    hood = "Golden Yellow Hood"
    if (selectedFaculty.value === 'Laws') hood = "Purple Hood"
    if (selectedFaculty.value === 'Business Administration') hood = "Drab Hood"
    
    hat = selectedLevel.value === 'phd' ? "Black Bonnet with Gold Tassel" : "Black Mortarboard with Tassel"
  }

  if (type === 'elite') {
    return [
      "Luxury Velvet-Touch Finish",
      `Premium ${hood}`,
      `Custom-tailored ${gown}`,
      `Premium ${hat}`
    ]
  }

  return [hood, gown, hat]
}

const classicFeatures = computed(() => getPackageFeatures('classic'))
const eliteFeatures = computed(() => getPackageFeatures('elite'))

const selectedPackage = ref(null)

const selectPackage = (type) => {
  const isElite = type === 'elite'
  selectedPackage.value = {
    type,
    title: `${formattedLevel.value} ${isElite ? 'Elite' : 'Classic'}`,
    subtitle: `${formattedLevel.value.toUpperCase()} STANDARD`,
    price: isElite ? 85 : 65,
    features: isElite ? eliteFeatures.value : classicFeatures.value,
    shortDesc: isElite 
      ? "Luxury velvet-touch finish with custom-lined hood and premium tailoring."
      : `Standard ${formattedLevel.value} regalia featuring the traditional institution style.`,
    longDesc: isElite
      ? `The ${formattedLevel.value} Elite Collection provides the highest quality materials including velvet-touch finishes and a double-lined discipline-specific hood. The gown is constructed with reinforced shoulder fluting and a professional silhouette.`
      : `The ${formattedLevel.value} Classic Collection provides the iconic oblong sleeves and discipline-specific hood. The gown is constructed with reinforced shoulder fluting and a professional silhouette.`
  }
}

const proceedToOrder = () => {
  router.push({
    path: '/order',
    query: {
      title: selectedPackage.value.title,
      price: selectedPackage.value.price,
      level: formattedLevel.value
    }
  })
}

watch(() => route.query.new, (newVal) => {
  if (newVal === 'true') {
    selectedLevel.value = ''
    selectedInstitution.value = ''
    selectedFaculty.value = ''
    selectedPackage.value = null
    // Clean up url directly to prevent refresh-stickiness
    router.replace({ path: '/inventory' })
  }
}, { immediate: true })

</script>

<template>
  <div class="inventory-page pt-5">
    <!-- Package Details Overlay Screen -->
    <div v-if="selectedPackage" class="container py-4 fade-in">
      <button @click="selectedPackage = null" class="btn btn-link text-dark text-decoration-none p-0 mb-4 fw-medium fs-5">
        <i class="bi bi-arrow-left me-2"></i> Back to Collections
      </button>
      
      <div class="row g-5">
        <!-- Left Column: Image Card -->
        <div class="col-lg-5 position-relative">
          <div class="sticky-top" style="top: 100px;">
            <div class="card border-0 rounded-4 shadow-sm bg-white d-flex flex-column align-items-center justify-content-center p-5 position-relative" style="height: 500px;">
              <span class="badge bg-warning text-white rounded-pill px-4 py-2 position-absolute top-0 start-0 m-4 fw-bold mt-4 ms-4 shadow-sm" style="letter-spacing: 1px;">
                {{ formattedLevel.toUpperCase() }} COLLECTION
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
          
          <hr class="mb-4 d-none d-lg-block border-0 opacity-0">
          
          <button @click="proceedToOrder" class="btn btn-warning text-white fw-bold rounded-4 py-3 fs-5 w-100 btn-hover-custom mb-3">
            Select Rental Dates <i class="bi bi-calendar-event ms-2"></i>
          </button>
          <div class="d-flex gap-2 text-secondary align-items-center justify-content-center">
            <i class="bi bi-info-circle small"></i>
            <span class="small fw-bold" style="letter-spacing: 1px;">SECURE YOUR DATE EARLY. STANDARD 3-DAY RENTAL PERIOD APPLIES.</span>
          </div>
        </div>
      </div>
    </div>


    <div v-else class="container text-center py-4 fade-in">
      <h1 class="fw-bold display-4 mb-3 text-dark mt-2">Start Your Gown Rental</h1>
      <p class="text-secondary fs-5 mb-5">Please follow the selection flow to find the correct regalia for your ceremony.</p>

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
              <option value="bachelor">Bachelor's Degree</option>
              <option value="master">Master's Degree</option>
              <option value="phd">PhD</option>
            </select>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="col-md-4">
          <div class="card bg-white border-0 shadow-sm h-100 rounded-4 text-start p-4" :class="{ 'step-inactive': !isStep2Enabled }">
            <div class="d-flex align-items-center gap-2 mb-3 fw-bold" :class="isStep2Enabled ? 'text-warning' : 'text-warning-muted'">
              <i class="bi bi-building"></i>
              <span>STEP 2</span>
            </div>
            <label class="form-label mb-2 fs-6" :class="isStep2Enabled ? 'text-secondary' : 'text-muted'">Institution</label>
            <select v-model="selectedInstitution" :disabled="!isStep2Enabled" :class="isStep2Enabled ? 'bg-light-beige text-dark' : 'bg-light-beige-muted text-muted'" class="form-select custom-select rounded-pill border-0 shadow-none w-100 px-3 py-2">
              <option value="" disabled>Select Institution</option>
              <option v-for="inst in institutions" :key="inst" :value="inst">{{ inst }}</option>
            </select>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="col-md-4">
          <div class="card bg-white border-0 shadow-sm h-100 rounded-4 text-start p-4" :class="{ 'step-inactive': !isStep3Enabled }">
            <div class="d-flex align-items-center gap-2 mb-3 fw-bold" :class="isStep3Enabled ? 'text-warning' : 'text-warning-muted'">
              <i class="bi bi-briefcase"></i>
              <span>STEP 3</span>
            </div>
            <label class="form-label mb-2 fs-6" :class="isStep3Enabled ? 'text-secondary' : 'text-muted'">Faculty</label>
            <select v-model="selectedFaculty" :disabled="!isStep3Enabled" :class="isStep3Enabled ? 'bg-light-beige text-dark' : 'bg-light-beige-muted text-muted'" class="form-select custom-select rounded-pill border-0 shadow-none w-100 px-3 py-2">
              <option value="" disabled>Select Faculty</option>
              <option v-for="faculty in faculties" :key="faculty" :value="faculty">{{ faculty }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Placeholder Areas or Results -->
      <div v-if="!showResults" class="empty-state-box d-flex flex-column align-items-center justify-content-center mx-auto rounded-5 border-dashed">
        <i class="bi bi-mortarboard empty-icon mb-3"></i>
        <h5 class="fw-bold text-secondary">Select your institution details to view packages</h5>
      </div>

      <div v-else class="results-section fade-in">
        <h2 class="fw-bold text-dark mb-5 text-center">Available {{ formattedLevel }} Packages</h2>
        
        <div class="row g-4 justify-content-center mx-auto max-w-1000">
          
          <!-- Classic Package Card -->
          <div class="col-md-6 col-lg-5">
            <div class="card package-card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
              <div class="card-header bg-light-beige border-0 position-relative d-flex justify-content-center align-items-center p-5">
                <span class="price-tag badge bg-warning text-white rounded-pill px-3 py-2 fs-6 fw-bold position-absolute top-0 end-0 mt-3 me-3">$65</span>
                <div class="icon-box bg-white rounded-4 shadow-sm d-flex justify-content-center align-items-center">
                  <i class="bi bi-mortarboard fs-1 text-warning-custom"></i>
                </div>
              </div>
              <div class="card-body p-4 text-start d-flex flex-column">
                <h4 class="fw-bold mb-1 text-dark">{{ formattedLevel }} Classic</h4>
                <p class="text-secondary small mb-3">{{ selectedInstitution }} - {{ selectedFaculty }}</p>
                <p class="text-muted small mb-4">Standard {{ formattedLevel.toLowerCase() }} regalia featuring the traditional institution style.</p>
                
                <ul class="list-unstyled mb-5 d-flex flex-column gap-3">
                  <li v-for="(feature, idx) in classicFeatures" :key="'classic-'+idx" class="d-flex align-items-start gap-2">
                    <i class="bi bi-check-circle text-warning-custom mt-1"></i>
                    <span class="text-secondary fs-6">{{ feature }}</span>
                  </li>
                </ul>
                
                <button @click="selectPackage('classic')" class="btn btn-warning text-white fw-bold rounded-3 py-3 mt-auto fs-6 w-100 btn-hover-custom">
                  View Details <i class="bi bi-arrow-right ms-1"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Elite Package Card -->
          <div class="col-md-6 col-lg-5">
            <div class="card package-card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
              <div class="card-header bg-light-beige border-0 position-relative d-flex justify-content-center align-items-center p-5">
                <span class="price-tag badge bg-warning text-white rounded-pill px-3 py-2 fs-6 fw-bold position-absolute top-0 end-0 mt-3 me-3">$85</span>
                <div class="icon-box bg-white rounded-4 shadow-sm d-flex justify-content-center align-items-center">
                  <i class="bi bi-mortarboard fs-1 text-warning-custom"></i>
                </div>
              </div>
              <div class="card-body p-4 text-start d-flex flex-column">
                <h4 class="fw-bold mb-1 text-dark">{{ formattedLevel }} Elite</h4>
                <p class="text-secondary small mb-3">{{ selectedInstitution }} - {{ selectedFaculty }}</p>
                <p class="text-muted small mb-4">Luxury velvet-touch finish with custom-lined hood and premium tailoring.</p>
                
                <ul class="list-unstyled mb-5 d-flex flex-column gap-3">
                  <li v-for="(feature, idx) in eliteFeatures" :key="'elite-'+idx" class="d-flex align-items-start gap-2">
                    <i class="bi bi-check-circle text-warning-custom mt-1"></i>
                    <span class="text-secondary fs-6">{{ feature }}</span>
                  </li>
                </ul>
                
                <button @click="selectPackage('elite')" class="btn btn-warning text-white fw-bold rounded-3 py-3 mt-auto fs-6 w-100 btn-hover-custom">
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
</style>