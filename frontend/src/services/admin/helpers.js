import { clearCached, readCached, writeCached } from '../cache.js'

const ORDER_LIST_TTL_MS = 15 * 1000
const EMAIL_STATUS_TTL_MS = 30 * 1000

export function normalizeOrder(raw = {}) {
  const damagedItems = Array.isArray(raw.damaged_items) ? raw.damaged_items : []
  const derivedDamageSummary = damagedItems.length
    ? damagedItems.map(item => `${item.modelId || 'Item'} x${item.qty || 1}`).join(', ')
    : ''

  return {
    ...raw,
    orderID: raw.orderID ?? raw.order_id ?? raw.id ?? '',
    CustomerName: raw.CustomerName ?? raw.student_name ?? raw.customer_name ?? '',
    CustomerEmail: raw.CustomerEmail ?? raw.email ?? '',
    GownName:
      raw.GownName ??
      raw.gown_name ??
      (Array.isArray(raw.selected_items) && raw.selected_items.length
        ? raw.selected_items.map(item => item.itemName || item.modelId || 'Gown Item').join(', ')
        : raw.package_id || 'Graduation Package'),
    TotalAmount: raw.TotalAmount ?? raw.total_amount ?? 0,
    rental_start_date: raw.rental_start_date ?? raw.rentalStartDate ?? '',
    rental_end_date: raw.rental_end_date ?? raw.rentalEndDate ?? '',
    returned_at: raw.returned_at ?? raw.updated_at ?? raw.return_date ?? raw.rental_end_date ?? '',
    damage_status: raw.damage_status ?? (raw.status === 'RETURNED_DAMAGED' || raw.damaged ? 2 : 0),
    damage_to_item: raw.damage_to_item ?? raw.damage_report ?? derivedDamageSummary
  }
}

function formatFetchError(error, fallbackMessage) {
  if (error instanceof TypeError) {
    return new Error(`${fallbackMessage} The service may be unavailable right now.`)
  }
  return error instanceof Error ? error : new Error(fallbackMessage)
}

function resolveBrowserSafeBaseUrl(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  }

  if (baseUrl.includes('localhost:8081')) {
    return baseUrl.replace('localhost:8081', 'localhost:8000')
  }

  if (baseUrl.includes('localhost:5001')) {
    return baseUrl.replace('localhost:5001', 'localhost:8000')
  }

  return baseUrl
}

function resolveBrowserSafeOrderApiUrl(orderApiUrl) {
  return resolveBrowserSafeBaseUrl(orderApiUrl)
}

export function clearAdminOrderCaches() {
  clearCached('admin:orders:CONFIRMED')
  clearCached('admin:orders:ACTIVE')
  clearCached('admin:orders:RETURNED')
  clearCached('admin:orders:RETURNED_DAMAGED')
  clearCached('admin:orders:COMPLETED')
}

export async function fetchOrdersByStatus(orderApiUrl, status) {
  try {
    const safeBaseUrl = resolveBrowserSafeOrderApiUrl(orderApiUrl)
    const cacheKey = `admin:orders:${status}`
    const cached = readCached(cacheKey, ORDER_LIST_TTL_MS)
    if (cached) return cached

    const response = await fetch(`${safeBaseUrl}/orders/status/${encodeURIComponent(status)}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch ${status} orders`)
    }
    const data = await response.json()
    return writeCached(cacheKey, Array.isArray(data) ? data.map(normalizeOrder) : [])
  } catch (error) {
    throw formatFetchError(error, `Unable to load ${status.toLowerCase()} orders.`)
  }
}

export async function fetchEmailStatusForOrder(orderId, notificationApiUrl) {
  if (!orderId) return 'NOT SENT'

  const safeBaseUrl = resolveBrowserSafeBaseUrl(
    notificationApiUrl ||
      import.meta.env.VITE_NOTIFICATION_API_BASE_URL ||
      import.meta.env.VITE_API_BASE_URL ||
      'http://localhost:8000'
  )

  try {
    const cacheKey = `admin:email-status:${orderId}`
    const cached = readCached(cacheKey, EMAIL_STATUS_TTL_MS)
    if (cached) return cached

    const response = await fetch(`${safeBaseUrl}/notifications/${encodeURIComponent(orderId)}`)
    if (!response.ok) {
      return 'UNKNOWN'
    }

    const logs = await response.json()
    if (!Array.isArray(logs) || logs.length === 0) {
      return 'NOT SENT'
    }

    const emailLogs = logs.filter(log => log?.channel === 'EMAIL')
    if (!emailLogs.length) {
      return 'NOT SENT'
    }

    const latest = emailLogs.sort((a, b) => new Date(b?.created_at || 0) - new Date(a?.created_at || 0))[0]
    const rawEventType = String(latest?.event_type || '').toUpperCase()
    const rawStatus = String(latest?.status || '').toUpperCase()

    const stageByEventType = {
      CONFIRMATION: 'CONFIRMATION',
      COLLECTION: 'COLLECTION',
      RETURN: 'RETURN',
      DEPOSIT: 'DEPOSIT',
      ORDERCONFIRMED: 'CONFIRMATION',
      PICKUP_REMINDER: 'COLLECTION',
      RETURN_REMINDER: 'RETURN',
      RETURNPROCESSED: 'DEPOSIT'
    }

    const stage = stageByEventType[rawEventType] || 'UNKNOWN'
    if (stage === 'UNKNOWN') {
      return writeCached(cacheKey, rawStatus || 'UNKNOWN')
    }
    return writeCached(cacheKey, rawStatus === 'SENT' ? stage : `${stage} (${rawStatus || 'UNKNOWN'})`)
  } catch {
    return 'UNKNOWN'
  }
}
