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
  
    /**
   * Confirm order from pending to confirmed.
   * Needs backend order-service support.
   * Expected order-service endpoint:
   * PUT /orders/:orderId/status
   * body: { status: "CONFIRMED" }
   */
  async confirmOrder(orderId) {
    const ORDER_API_BASE_URL = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    try {
      const response = await fetch(`${ORDER_API_BASE_URL}/orders/${orderId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'CONFIRMED' }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.error || `HTTP ${response.status}: Failed to confirm order`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error confirming order:', error)
      throw error
    }
  }

  /**
   * Mark active order for return queue.
   * This is NOT implemented in the saga you showed.
   * For now this assumes order-service supports direct status update.
   * Expected backend endpoint:
   * PUT /orders/:orderId/status
   * body: { status: "RETURNED_PENDING_INSPECTION" }
   */
  async markForReturn(orderId) {
    const ORDER_API_BASE_URL = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'
    try {
      const response = await fetch(`${ORDER_API_BASE_URL}/orders/${orderId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'RETURNED_PENDING_INSPECTION' }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.error || `HTTP ${response.status}: Failed to mark for return`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error marking order for return:', error)
      throw error
    }
  }

  /**
   * Process return-repair action from queue page.
   * Existing saga only supports:
   * - processReturn()
   * - transitionToWash()
   * - maintenanceComplete()
   * So this method routes to what already exists.
   */
  async processReturnRepair(orderId, action, notes = '') {
    if (action === 'repair') {
      return this.processReturn({
        order_id: orderId,
        damage_report: notes,
        damage_fee: 0,
      })
    }

    if (action === 'wash') {
      return this.transitionToWash(orderId)
    }

    if (action === 'complete') {
      return this.maintenanceComplete(orderId)
    }

    throw new Error('Invalid repair action')
  }

  /**
   * Used by MaintenancePage.vue
   * Existing saga endpoint:
   * PUT /returns/transition-to-wash
   */
  async completeRepair(orderId) {
    return this.transitionToWash(orderId)
  }

  /**
   * Used by MaintenancePage.vue
   * Existing saga endpoint:
   * PUT /returns/maintenance-complete
   */
  async completeWash(orderId) {
    return this.maintenanceComplete(orderId)
  }

  /**
   * Placeholder wrapper for pages that mark the item/order fully done.
   * Uses existing maintenance completion saga.
   */
  async markItemComplete(orderId) {
    return this.maintenanceComplete(orderId)
  }
}

export default new AdminService()
