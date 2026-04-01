<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">
          <i class="bi bi-shield-lock"></i>
        </div>
        <h1>Admin Login</h1>
        <p>Gown Rental Administration Portal</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input
            v-model="credentials.username"
            type="text"
            class="form-control"
            id="username"
            placeholder="Enter username"
            required
          />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            v-model="credentials.password"
            type="password"
            class="form-control"
            id="password"
            placeholder="Enter password"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-danger alert-sm mt-3" role="alert">
        <i class="bi bi-exclamation-circle me-2"></i>
        {{ error }}
      </div>

      <!-- Info Message -->
      <div class="alert alert-info alert-sm mt-3" role="alert">
        <i class="bi bi-info-circle me-2"></i>
        <strong>Demo Credentials:</strong><br />
        Username: <code>admin</code><br />
        Password: <code>admin123</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthService from '../services/auth'

const router = useRouter()

const credentials = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const result = await AuthService.login(credentials.value.username, credentials.value.password)
    
    if (result.success) {
      // Redirect to admin dashboard
      router.push('/admin')
    } else {
      error.value = result.message
    }
  } catch (err) {
    error.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fbf7ef;
  padding: 1rem;
  padding-top: 100px;
}

.login-card {
  background: white;
  border-radius: 20px;
  border: none;
  padding: 2.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-icon {
  font-size: 3.5rem;
  color: #d8a61c;
  margin-bottom: 1rem;
}

.login-header h1 {
  font-size: 1.75rem;
  color: #2b3035;
  margin: 0.75rem 0 0.5rem;
  font-weight: 700;
}

.login-header p {
  color: #6c757d;
  margin: 0;
  font-size: 0.95rem;
}

.form-label {
  font-weight: 600;
  color: #2b3035;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.form-control {
  border-radius: 12px;
  border: 1px solid #e9ecef;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  background-color: #f6efe1;
  color: #2b3035;
}

.form-control::placeholder {
  color: #aaa;
}

.form-control:focus {
  border-color: #d8a61c;
  background-color: #f6efe1;
  box-shadow: 0 0 0 0.2rem rgba(216, 166, 28, 0.15);
  color: #2b3035;
}

.btn-primary {
  background-color: #d8a61c;
  border-color: #d8a61c;
  padding: 0.85rem;
  font-weight: 700;
  border-radius: 12px;
  font-size: 1rem;
}

.btn-primary:hover:not(:disabled) {
  background-color: #c49416;
  border-color: #c49416;
}

.btn-primary:disabled {
  opacity: 0.7;
}

.alert-sm {
  padding: 0.875rem 1rem;
  font-size: 0.9rem;
  margin: 0;
  border-radius: 12px;
  border: none;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

code {
  background-color: #f6efe1;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  color: #d8a61c;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}
</style>
