// Inventory Service API Client
// Handles all API calls to the inventory-service backend
 
import {
  GraduationPackage,
  DetailedPackage,
  Inventory,
  ItemHold,
  AvailabilityResponse,
  Availability90Response
} from './model.js'
 
const API_BASE_URL = import.meta.env.VITE_INVENTORY_API_BASE_URL || 'http://localhost:8080/api/inventory'
 
const unwrapApiData = (payload) => payload?.data ?? payload?.date ?? payload
 
class InventoryService {
  /**
   * Get a specific package by its ID
   * @param {string} packageId - The package ID
   * @returns {Promise<GraduationPackage>}
   */
  async getPackageById(packageId) {
    try {
      const response = await fetch(`${API_BASE_URL}/${packageId}`)
      if (!response.ok) throw new Error('Failed to fetch package')
      const payload = await response.json()
      const data = unwrapApiData(payload)
      return new DetailedPackage(data)
    } catch (error) {
      console.error('Error fetching package:', error)
      if (error instanceof TypeError) {
        throw new Error('Unable to load package details right now. Please try again shortly.')
      }
      throw error
    }
  }
 
  /**
   * Get all packages with optional filters
   * @param {Object} filters - Optional filters { institution, educationLevel, faculty }
   * @returns {Promise<GraduationPackage[]>}
   */
  async getAllPackages(filters = {}) {
    try {
      let url = `${API_BASE_URL}/catalogue`
      
      if (filters.institution) {
        url = `${API_BASE_URL}/catalogue?institution=${filters.institution}`
      }
      if (filters.educationLevel) {
        url += `${url.includes('?') ? '&' : '?'}educationLevel=${filters.educationLevel}`
      }
      if (filters.faculty) {
        url += `${url.includes('?') ? '&' : '?'}faculty=${filters.faculty}`
      }
 
      console.log('Fetching from:', url)
      const response = await fetch(url)
      if (!response.ok) throw new Error(`API returned ${response.status}: ${response.statusText}`)
      const apiResponse = await response.json()
      
      console.log('API Response:', apiResponse)
      
      const packagesData = unwrapApiData(apiResponse) || []
      
      if (!Array.isArray(packagesData)) {
        throw new Error('API response does not contain a valid package array')
      }
      
      const packages = packagesData.map(item => {
        if (!item.graduationPackageDto) {
          console.warn('Missing graduationPackageDto in item:', item)
          return null
        }
        return new GraduationPackage(item.graduationPackageDto, {
          totalDeposit: item.totalDeposit,
          totalRentalFee: item.totalRentalFee,
          totalPrice: item.totalPrice
        })
      }).filter(pkg => pkg !== null)
      
      console.log('Parsed packages count:', packages.length)
      return packages
    } catch (error) {
      console.error('Error fetching packages:', error)
      if (error instanceof TypeError) {
        throw new Error('Unable to load inventory packages right now. Please try again shortly.')
      }
      throw error
    }
  }
 
  /**
   * Get availability for specific models on a given date
   * @param {Object} modelIds - { hatModelId, hoodModelId, gownModelId }
   * @param {string} date - Date in format YYYY-MM-DD
   * @returns {Promise<AvailabilityResponse>}
   */
  async checkAvailability(modelIds, date) {
    try {
      const params = new URLSearchParams({ date })
      if (modelIds.hatModelId) params.set('hatModelId', modelIds.hatModelId)
      if (modelIds.hoodModelId) params.set('hoodModelId', modelIds.hoodModelId)
      if (modelIds.gownModelId) params.set('gownModelId', modelIds.gownModelId)

      const response = await fetch(`${API_BASE_URL}/availability?${params}`)
      if (!response.ok) throw new Error('Failed to check availability')
      const payload = await response.json()
      const data = unwrapApiData(payload)
      return new AvailabilityResponse(data)
    } catch (error) {
      console.error('Error checking availability:', error)
      if (error instanceof TypeError) {
        throw new Error('Unable to load inventory availability right now. Please try again shortly.')
      }
      throw error
    }
  }
 
  /**
   * Get 90-day availability for specific models
   * @param {Object} modelIds - { hatModelId, hoodModelId, gownModelId }
   * @returns {Promise<Availability90Response[]>}
   */
  async checkAvailability90Days(modelIds) {
    try {
      const params = new URLSearchParams({
        hatModelId: modelIds.hatModelId,
        hoodModelId: modelIds.hoodModelId,
        gownModelId: modelIds.gownModelId
      })
 
      const response = await fetch(`${API_BASE_URL}/availability90?${params}`)
      if (!response.ok) throw new Error('Failed to check 90-day availability')
      const payload = await response.json()
      const data = unwrapApiData(payload)
      
      return Array.isArray(data) ? data.map(item => new Availability90Response(item)) : [new Availability90Response(data)]
    } catch (error) {
      console.error('Error checking 90-day availability:', error)
      throw error
    }
  }
 
  /**
   * Soft-lock items (reserves for 10 minutes)
   * @param {Array} items - Array of { modelId, qty, chosenDate }
   * @returns {Promise<ItemHold>}
   */
  async softLockItems(items) {
    try {
      const response = await fetch(`${API_BASE_URL}/soft-hold`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(items)
      })
      
      if (!response.ok) throw new Error('Failed to soft-lock items')
      const payload = await response.json()
      const data = unwrapApiData(payload)
      return new ItemHold(data)
    } catch (error) {
      console.error('Error soft-locking items:', error)
      throw error
    }
  }
 
  /**
   * Reserve items after purchase
   * @param {string} holdId - The hold ID from soft-lock
   * @param {Array} items - Array of { modelId, qty, chosenDate }
   * @returns {Promise<Object>}
   */
  async reserveItems(holdId, items) {
    try {
      const response = await fetch(`${API_BASE_URL}/reserveitems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ holdId, items })
      })
      
      if (!response.ok) throw new Error('Failed to reserve items')
      const payload = await response.json()
      return unwrapApiData(payload)
    } catch (error) {
      console.error('Error reserving items:', error)
      throw error
    }
  }
 
  /**
   * Mark items as collected by customer
   * @param {Array} items - Array of { modelId, qty, chosenDate }
   * @returns {Promise<Object>}
   */
  async collectItems(items) {
    try {
      const response = await fetch(`${API_BASE_URL}/collectitems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(items)
      })
      
      if (!response.ok) throw new Error('Failed to collect items')
      const payload = await response.json()
      return unwrapApiData(payload)
    } catch (error) {
      console.error('Error collecting items:', error)
      throw error
    }
  }
 
  /**
   * Mark items for washing after return
   * @param {Array} items - Array of { modelId, qty, chosenDate }
   * @returns {Promise<Object>}
   */
  async washItems(items) {
    try {
      const response = await fetch(`${API_BASE_URL}/washitems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(items)
      })
      
      if (!response.ok) throw new Error('Failed to send items to wash')
      const payload = await response.json()
      return unwrapApiData(payload)
    } catch (error) {
      console.error('Error washing items:', error)
      throw error
    }
  }

  async getStockOverview(date = new Date()) {
    try {
      const dateParam = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Singapore',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }).format(new Date(date))

      const response = await fetch(`${API_BASE_URL}/stock-overview?date=${dateParam}`)
      if (!response.ok) throw new Error('Failed to fetch stock overview')
      const payload = await response.json()
      const data = unwrapApiData(payload) || []

      if (!Array.isArray(data)) {
        throw new Error('Inventory stock overview returned an invalid response.')
      }

      return data
        .map(row => ({
          modelId: row.modelId,
          itemName: row.itemName,
          itemType: row.itemType,
          size: row.size,
          totalQty: Number(row.totalQty || 0),
          availableQty: Number(row.availableQty || 0),
          reservedQty: Number(row.reservedQty || 0),
          rentedQty: Number(row.rentedQty || 0),
          damagedQty: Number(row.damagedQty || 0),
          repairQty: Number(row.repairQty || 0),
          washQty: Number(row.washQty || 0),
          backupQty: Number(row.backupQty || 0)
        }))
        .sort((a, b) => a.modelId.localeCompare(b.modelId))
    } catch (error) {
      console.error('Error loading stock overview:', error)
      if (error instanceof TypeError) {
        throw new Error('Unable to load live stock counts right now. Please try again shortly.')
      }
      throw error
    }
  }
}
 
// Export singleton instance
export default new InventoryService()
