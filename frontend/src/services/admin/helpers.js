export function normalizeOrder(raw = {}) {
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
    damage_status: raw.damage_status ?? 0,
    damage_to_item: raw.damage_to_item ?? raw.damage_report ?? ''
  }
}

export async function fetchOrdersByStatus(orderApiUrl, status) {
  const response = await fetch(`${orderApiUrl}/orders/status/${encodeURIComponent(status)}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch ${status} orders`)
  }
  const data = await response.json()
  return Array.isArray(data) ? data.map(normalizeOrder) : []
}