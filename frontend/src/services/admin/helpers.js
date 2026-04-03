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

export async function fetchOrdersByStatus(orderApiUrl, status) {
  try {
    const response = await fetch(`${orderApiUrl}/orders/status/${encodeURIComponent(status)}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch ${status} orders`)
    }
    const data = await response.json()
    return Array.isArray(data) ? data.map(normalizeOrder) : []
  } catch (error) {
    throw formatFetchError(error, `Unable to load ${status.toLowerCase()} orders.`)
  }
}
