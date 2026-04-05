const SAGA_API_BASE_URL = import.meta.env.VITE_SAGA_API_BASE_URL || 'http://localhost:8000'
const ORDER_API_BASE_URL = import.meta.env.VITE_ORDER_API_BASE_URL || 'http://localhost:8000'

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

  async getOrdersByEmail(email) {
    return requestJson(`${ORDER_API_BASE_URL}/orders/by-email/${encodeURIComponent(email)}`)
  }
}

export default new OrderService()
