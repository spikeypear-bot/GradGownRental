const LOGISTICS_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function formatFetchError(error, fallbackMessage) {
  if (error instanceof TypeError) {
    return new Error(`${fallbackMessage} The service may be unavailable right now.`)
  }
  return error instanceof Error ? error : new Error(fallbackMessage)
}

class LogisticsService {
  async getShipment(shipmentId) {
    try {
      const response = await fetch(`${LOGISTICS_API_BASE_URL}/logistics/${encodeURIComponent(shipmentId)}`)
      const payload = await response.json().catch(() => ({}))

      if (!response.ok) {
        const message = payload?.error || payload?.message || `Failed to load shipment ${shipmentId}`
        throw new Error(message)
      }

      return payload
    } catch (error) {
      throw formatFetchError(error, `Unable to load shipment ${shipmentId}.`)
    }
  }

  async getShipments(orderIds = []) {
    const uniqueIds = [...new Set(orderIds.filter(Boolean))]

    const shipments = await Promise.all(
      uniqueIds.map(async (orderId) => {
        try {
          return await this.getShipment(orderId)
        } catch (error) {
          if (error.message?.toLowerCase().includes('not found')) {
            return null
          }
          throw error
        }
      })
    )

    return shipments.filter(Boolean)
  }
}

export default new LogisticsService()
