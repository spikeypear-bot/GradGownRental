// Admin Service API Client
// Handles all admin operations: fulfillment and returns

const FULFILLMENT_API_BASE_URL = import.meta.env.VITE_FULFILLMENT_API_BASE_URL || 'http://localhost:8084/fulfillment'
const RETURN_API_BASE_URL = import.meta.env.VITE_RETURN_API_BASE_URL || 'http://localhost:8085/returns'

class AdminService {
  /**
   * Activate fulfillment (collection/delivery)
   * @param {string} orderId - The order ID
   * @returns {Promise<Object>}
   */
  async activateFulfillment(orderId) {
    try {
      const response = await fetch(`${FULFILLMENT_API_BASE_URL}/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order_id: orderId })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || `HTTP ${response.status}: Failed to activate fulfillment`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error activating fulfillment:', error)
      throw error
    }
  }

  /**
   * Process a gown return (damaged/normal)
   * @param {Object} returnData - { order_id, damage_report?, damage_fee? }
   * @returns {Promise<Object>}
   */
  async processReturn(returnData) {
    try {
      const response = await fetch(`${RETURN_API_BASE_URL}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(returnData)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || `HTTP ${response.status}: Failed to process return`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error processing return:', error)
      throw error
    }
  }

  /**
   * Transition gown to wash (after repair)
   * @param {string} orderId - The order ID
   * @returns {Promise<Object>}
   */
  async transitionToWash(orderId) {
    try {
      const response = await fetch(`${RETURN_API_BASE_URL}/transition-to-wash`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order_id: orderId })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || `HTTP ${response.status}: Failed to transition to wash`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error transitioning to wash:', error)
      throw error
    }
  }

  /**
   * Complete maintenance (washing done, ready for inventory)
   * @param {string} orderId - The order ID
   * @returns {Promise<Object>}
   */
  async maintenanceComplete(orderId) {
    try {
      const response = await fetch(`${RETURN_API_BASE_URL}/maintenance-complete`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ order_id: orderId })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || `HTTP ${response.status}: Failed to complete maintenance`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error completing maintenance:', error)
      throw error
    }
  }
}

export default new AdminService()
