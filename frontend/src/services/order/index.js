const SAGA_API_BASE_URL = import.meta.env.VITE_SAGA_API_BASE_URL || 'http://localhost:5003'
const ORDER_API_BASE_URL = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8081'

async function requestJson(url, options = {}) {
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
}

class OrderService {
  async createOrder(payload) {
    return requestJson(`${SAGA_API_BASE_URL}/orders/create`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  async submitPayment(payload) {
    return requestJson(`${SAGA_API_BASE_URL}/submit-payment`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }

  async getOrder(orderId) {
    return requestJson(`${ORDER_API_BASE_URL}/orders/${orderId}`)
  }

  async activateOrder(orderId) {
    return requestJson(`${ORDER_API_BASE_URL}/orders/${orderId}/activate`, {
      method: 'POST'
    })
  }

  async returnOrder(orderId, damagedItems = []) {
    return requestJson(`${ORDER_API_BASE_URL}/orders/${orderId}/return`, {
      method: 'POST',
      body: JSON.stringify({ damaged_items: damagedItems })
    })
  }

  async getOrdersByEmail(email) {
    return requestJson(`${ORDER_API_BASE_URL}/orders/by-email/${encodeURIComponent(email)}`)
  }
}

export default new OrderService()
