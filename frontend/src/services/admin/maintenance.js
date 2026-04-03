import { fetchOrdersByStatus } from './helpers'

const STORAGE_KEY = 'admin-maintenance-stages'

export function readStageMap() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

export function writeStageMap(stageMap) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stageMap))
}

export function mapOrderToMaintenanceItem(order, stage) {
  return {
    id: order.orderID,
    itemId: order.orderID,
    gownName: order.GownName,
    issue: order.damage_to_item || 'Damaged item recorded',
    condition: stage === 'wash' ? 'Repaired and waiting for wash completion' : 'Damaged return awaiting repair',
    dateAdded: order.returned_at || order.updated_at || new Date().toISOString(),
    washDate: order.completed_at || new Date().toISOString()
  }
}

export async function loadMaintenanceBuckets(orderApiUrl) {
  const stageMap = readStageMap()
  const [damagedOrders, completedOrders] = await Promise.all([
    fetchOrdersByStatus(orderApiUrl, 'RETURNED_DAMAGED'),
    fetchOrdersByStatus(orderApiUrl, 'COMPLETED')
  ])

  return {
    repairQueue: damagedOrders
      .filter(order => (stageMap[order.orderID] || 'repair') === 'repair')
      .map(order => mapOrderToMaintenanceItem(order, 'repair')),
    washQueue: damagedOrders
      .filter(order => stageMap[order.orderID] === 'wash')
      .map(order => mapOrderToMaintenanceItem(order, 'wash')),
    completedQueue: completedOrders
      .filter(order => order.damaged || order.damage_status > 0)
      .slice(0, 10)
      .map(order => mapOrderToMaintenanceItem(order, 'ready'))
  }
}
