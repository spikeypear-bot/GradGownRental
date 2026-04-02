// Admin Auth Service
// Manages admin login/logout and authentication state

const AUTH_STORAGE_KEY = 'admin_auth_token'
const DEFAULT_ADMIN_PASSWORD = 'admin123'  // In production, this should be stored securely in backend

class AuthService {
  /**
   * Login with admin credentials
   * @param {string} username - Admin username
   * @param {string} password - Admin password
   * @returns {Promise<Object>} - { success, token, message }
   */
  async login(username, password) {
    // Simulate backend auth (in production, call actual backend endpoint)
    return new Promise((resolve) => {
      setTimeout(() => {
        // Simple validation - in production use secure backend auth
        if (username === 'admin' && password === DEFAULT_ADMIN_PASSWORD) {
          const token = btoa(`${username}:${password}:${Date.now()}`)
          localStorage.setItem(AUTH_STORAGE_KEY, token)
          resolve({
            success: true,
            token,
            message: 'Login successful'
          })
        } else {
          resolve({
            success: false,
            token: null,
            message: 'Invalid username or password'
          })
        }
      }, 300)
    })
  }

  /**
   * Logout admin
   */
  logout() {
    localStorage.removeItem(AUTH_STORAGE_KEY)
  }

  /**
   * Check if admin is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem(AUTH_STORAGE_KEY)
  }

  /**
   * Get current auth token
   * @returns {string|null}
   */
  getToken() {
    return localStorage.getItem(AUTH_STORAGE_KEY)
  }
}

export default new AuthService()
