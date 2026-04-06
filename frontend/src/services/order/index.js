const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
import { clearCached, readCached, writeCached } from '../cache.js'
const ORDER_DETAIL_TTL_MS = 15 * 1000

async function requestJson(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    })

    let payload = {}
    try {
      payload = await response.json()
    } catch {
      payload = {}
    }

    if (!response.ok) {
      const message = payload?.error || `Request failed with status ${response.status}`
      throw new Error(message)
    }

    return payload
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Unable to reach the service right now. Please try again shortly.')
    }
    throw error
  }
}

class OrderService {
  async createOrder(payload) {
    clearCached(`order:detail:${payload?.order_id || ''}`)
    return requestJson(`${API_BASE_URL}/orders/create`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  async submitPayment(payload) {
    clearCached(`order:detail:${payload?.order_id || ''}`)
    return requestJson(`${API_BASE_URL}/submit-payment`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  async getOrder(orderId) {
    const cacheKey = `order:detail:${orderId}`
    const cached = readCached(cacheKey, ORDER_DETAIL_TTL_MS)
    if (cached) return cached
    return writeCached(cacheKey, await requestJson(`${API_BASE_URL}/orders/${orderId}`))
  }

  async getOrdersByEmail(email) {
    return requestJson(`${API_BASE_URL}/orders/by-email/${encodeURIComponent(email)}`)
  }
}

export default new OrderService()
