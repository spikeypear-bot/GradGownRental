// Admin Service API Client
// Handles all admin operations: fulfillment and returns
import { clearCached, readCached, writeCached } from '../cache.js'
import { clearAdminOrderCaches } from './helpers.js'

const withPathSuffix = (baseUrl, suffix) => {
  const normalizedBase = String(baseUrl || '').replace(/\/+$/, '')
  return normalizedBase.endsWith(suffix) ? normalizedBase : `${normalizedBase}${suffix}`
}

const FULFILLMENT_API_BASE_URL = withPathSuffix(
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  '/fulfillment'
)

const RETURN_API_BASE_URL = withPathSuffix(
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  '/returns'
)

const INVENTORY_API_BASE_URL = withPathSuffix(
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  '/api/inventory'
)

const LOGISTICS_API_BASE_URL = withPathSuffix(
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  '/logistics'
)
const SHIPMENT_TTL_MS = 15 * 1000

class AdminService {
  formatFetchError(error, fallbackMessage) {
    if (error instanceof TypeError) {
      return new Error(`${fallbackMessage} The service may be unavailable right now.`)
    }
    return error instanceof Error ? error : new Error(fallbackMessage)
  }

  async parseError(response, fallbackMessage) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.message || errorData.error || `HTTP ${response.status}: ${fallbackMessage}`)
  }

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
        await this.parseError(response, 'Failed to activate fulfillment')
      }

      clearAdminOrderCaches()
      clearCached(`logistics:shipment:${orderId}`)
      return await response.json()
    } catch (error) {
      console.error('Error activating fulfillment:', error)
      throw this.formatFetchError(error, 'Unable to activate fulfillment.')
    }
  }

  async getShipmentForOrder(orderId) {
    try {
      const cacheKey = `logistics:shipment:${orderId}`
      const cached = readCached(cacheKey, SHIPMENT_TTL_MS)
      if (cached !== null) {
        return cached
      }

      const response = await fetch(`${LOGISTICS_API_BASE_URL}/order/${encodeURIComponent(orderId)}`)

      if (response.status === 404) {
        writeCached(cacheKey, null)
        return null
      }

      if (!response.ok) {
        await this.parseError(response, 'Failed to load shipment details')
      }

      return writeCached(cacheKey, await response.json())
    } catch (error) {
      console.error('Error loading shipment details:', error)
      throw this.formatFetchError(error, 'Unable to load shipment details.')
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
        await this.parseError(response, 'Failed to process return')
      }

      clearAdminOrderCaches()
      clearCached(`logistics:shipment:${returnData?.order_id || ''}`)
      return await response.json()
    } catch (error) {
      console.error('Error processing return:', error)
      throw this.formatFetchError(error, 'Unable to process return.')
    }
  }

  /**
   * Transition gown to wash (after repair)
   * @param {string} orderId - The order ID
   * @returns {Promise<Object>}
   */
  async transitionToWash(orderId, selectedPackages = null) {
    try {
      const response = await fetch(`${RETURN_API_BASE_URL}/transition-to-wash`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          ...(selectedPackages ? { selected_packages: selectedPackages } : {}),
        })
      })

      if (!response.ok) {
        await this.parseError(response, 'Failed to transition to wash')
      }

      clearAdminOrderCaches()
      clearCached(`logistics:shipment:${orderId}`)
      return await response.json()
    } catch (error) {
      console.error('Error transitioning to wash:', error)
      throw this.formatFetchError(error, 'Unable to move the order to wash.')
    }
  }

  /**
   * Complete maintenance (washing done, ready for inventory)
   * @param {string} orderId - The order ID
   * @returns {Promise<Object>}
   */
  async maintenanceComplete(orderId, selectedPackages = null, options = {}) {
    try {
      const response = await fetch(`${RETURN_API_BASE_URL}/maintenance-complete`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_id: orderId,
          ...(selectedPackages ? { selected_packages: selectedPackages } : {}),
          ...(Object.prototype.hasOwnProperty.call(options, 'completeOrder')
            ? { complete_order: options.completeOrder }
            : {}),
        })
      })

      if (!response.ok) {
        await this.parseError(response, 'Failed to complete maintenance')
      }

      clearAdminOrderCaches()
      clearCached(`logistics:shipment:${orderId}`)
      return await response.json()
    } catch (error) {
      console.error('Error completing maintenance:', error)
      throw this.formatFetchError(error, 'Unable to complete maintenance.')
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
    // Per Scenario 3: order confirmation flows through the fulfillment saga
    return this.activateFulfillment(orderId)
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
    // Per Scenario 4: return initiation flows through the return saga
    return this.processReturn({ order_id: orderId })
  }

  /**
   * Process return-repair action from queue page.
   * Existing saga only supports:
   * - processReturn()
   * - transitionToWash()
   * - maintenanceComplete()
   * So this method routes to what already exists.
   */
  async processReturnRepair(orderId, action) {
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
  async completeRepair(orderId, selectedPackages = null) {
    return this.transitionToWash(orderId, selectedPackages)
  }

  /**
   * Used by MaintenancePage.vue
   * Existing saga endpoint:
   * PUT /returns/maintenance-complete
   */
  async completeWash(orderId, selectedPackages = null, options = {}) {
    return this.maintenanceComplete(orderId, selectedPackages, options)
  }

  async useBackupStock(order) {
    const selectedItems = Array.isArray(order?.selected_items) ? order.selected_items : []
    const chosenDate = order?.rental_start_date

    if (!selectedItems.length || !chosenDate) {
      throw new Error('This order is missing item or date details needed to activate backup stock.')
    }

    const items = selectedItems.map(item => ({
      modelId: item.modelId,
      qty: Number(item.qty || 1),
      chosenDate: item.chosenDate || chosenDate,
    }))

    if (items.some(item => !item.modelId || !item.chosenDate || item.qty <= 0)) {
      throw new Error('This order has incomplete item data, so backup stock could not be activated.')
    }

    try {
      const response = await fetch(`${INVENTORY_API_BASE_URL}/stock/transition`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transition: 'USE_BACKUP_FOR_FULFILLMENT',
          orderId: order.orderID || order.order_id,
          items,
        })
      })

      if (!response.ok) {
        await this.parseError(response, 'Failed to activate backup stock')
      }

      return await response.json()
    } catch (error) {
      console.error('Error activating backup stock:', error)
      throw this.formatFetchError(error, 'Unable to activate backup stock.')
    }
  }

  /**
   * Placeholder wrapper for pages that mark the item/order fully done.
   * Uses existing maintenance completion saga.
   */
  async markItemComplete(orderId, selectedPackages = null, options = {}) {
    return this.maintenanceComplete(orderId, selectedPackages, options)
  }
}

export default new AdminService()
