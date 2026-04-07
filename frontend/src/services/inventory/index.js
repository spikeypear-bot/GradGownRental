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
import { readCached, writeCached } from '../cache.js'
 
const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/inventory`
const PACKAGE_DETAIL_TTL_MS = 5 * 60 * 1000
const PACKAGE_LIST_TTL_MS = 5 * 60 * 1000
const STOCK_OVERVIEW_TTL_MS = 30 * 1000
 
const unwrapApiData = (payload) => {
  if (
    payload &&
    typeof payload === 'object' &&
    ('status' in payload || 'msg' in payload || 'data' in payload)
  ) {
    return payload?.data ?? payload?.date ?? null
  }
  return payload
}
 
class InventoryService {
  /**
   * Get a specific package by its ID
   * @param {string} packageId - The package ID
   * @returns {Promise<GraduationPackage>}
   */
  async getPackageById(packageId) {
    try {
      const cacheKey = `inventory:package:${packageId}`
      const cached = readCached(cacheKey, PACKAGE_DETAIL_TTL_MS)
      if (cached) return cached

      const response = await fetch(`${API_BASE_URL}/${packageId}`)
      if (!response.ok) throw new Error('Failed to fetch package')
      const payload = await response.json()
      const data = unwrapApiData(payload)
      return writeCached(cacheKey, new DetailedPackage(data))
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

      const cacheKey = `inventory:catalogue:${url}`
      const cached = readCached(cacheKey, PACKAGE_LIST_TTL_MS)
      if (cached) return cached
 
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
      return writeCached(cacheKey, packages)
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
      if (payload?.status && payload.status !== 200) {
        throw new Error(payload?.msg || 'Failed to check availability')
      }
      const data = unwrapApiData(payload)
      if (!data) {
        throw new Error(payload?.msg || 'Availability data is missing')
      }
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
      if (payload?.status && payload.status !== 200) {
        throw new Error(payload?.msg || 'Failed to check 90-day availability')
      }
      const data = unwrapApiData(payload)
      if (!data) {
        throw new Error(payload?.msg || '90-day availability data is missing')
      }
      
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
 
  async getStockOverview(date = new Date()) {
    try {
      const dateParam = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Singapore',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      }).format(new Date(date))

      const cacheKey = `inventory:stock-overview:${dateParam}`
      const cached = readCached(cacheKey, STOCK_OVERVIEW_TTL_MS)
      if (cached) return cached

      const response = await fetch(`${API_BASE_URL}/stock-overview?date=${dateParam}`)
      if (!response.ok) throw new Error('Failed to fetch stock overview')
      const payload = await response.json()
      const data = unwrapApiData(payload) || []

      if (!Array.isArray(data)) {
        throw new Error('Inventory stock overview returned an invalid response.')
      }

      const rows = data
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
          washQty: Number(row.washQty || 0),
          backupQty: Number(row.backupQty || 0)
        }))
        .sort((a, b) => a.modelId.localeCompare(b.modelId))
      return writeCached(cacheKey, rows)
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
