import { fetchOrdersByStatus } from './helpers'

const STORAGE_KEY = 'admin-maintenance-stages'
const DETAILS_KEY = 'admin-maintenance-details'

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

export function readMaintenanceDetails() {
  try {
    return JSON.parse(localStorage.getItem(DETAILS_KEY) || '{}')
  } catch {
    return {}
  }
}

export function writeMaintenanceDetails(detailsMap) {
  localStorage.setItem(DETAILS_KEY, JSON.stringify(detailsMap))
}

function buildQueueId(orderId, subsetKey, stage) {
  return `${orderId}:${subsetKey}:${stage}`
}

export function mapOrderToMaintenanceItem(order, stage, selectedPackages = [], subsetKey = stage) {
  const label = Array.isArray(selectedPackages) && selectedPackages.length
    ? selectedPackages.map(item => item.itemName || item.modelId || 'Gown Item').join(', ')
    : order.GownName
  return {
    id: buildQueueId(order.orderID, subsetKey, stage),
    itemId: order.orderID,
    gownName: label,
    issue: order.damage_to_item || 'Damaged item recorded',
    condition: stage === 'wash' ? 'Repaired and waiting for wash completion' : 'Damaged return awaiting repair',
    dateAdded: order.returned_at || order.updated_at || new Date().toISOString(),
    washDate: order.completed_at || new Date().toISOString(),
    selectedPackages,
    subsetKey
  }
}

export async function loadMaintenanceBuckets(orderApiUrl) {
  const detailsMap = readMaintenanceDetails()
  const [returnedOrders, damagedOrders, completedOrders] = await Promise.all([
    fetchOrdersByStatus(orderApiUrl, 'RETURNED'),
    fetchOrdersByStatus(orderApiUrl, 'RETURNED_DAMAGED'),
    fetchOrdersByStatus(orderApiUrl, 'COMPLETED')
  ])

  return {
    repairQueue: damagedOrders.flatMap(order => {
      const details = detailsMap[order.orderID] || {}
      const damagedPackages = details.damagedPackages || order.damaged_items || []
      const damagedStage = details.damagedStage || (damagedPackages.length ? 'repair' : null)
      if (!damagedPackages.length || damagedStage !== 'repair') {
        return []
      }
      return [mapOrderToMaintenanceItem(order, 'repair', damagedPackages, 'damaged')]
    }),
    washQueue: [
      ...returnedOrders.flatMap(order => {
        const details = detailsMap[order.orderID] || {}
        const cleanPackages = details.cleanPackages || details.allSelected || order.selected_items || []
        const cleanStage = details.cleanStage || (cleanPackages.length ? 'wash' : null)
        if (!cleanPackages.length || cleanStage !== 'wash') {
          return []
        }
        return [mapOrderToMaintenanceItem(order, 'wash', cleanPackages, 'clean')]
      }),
      ...damagedOrders.flatMap(order => {
        const details = detailsMap[order.orderID] || {}
        const entries = []
        const cleanPackages = details.cleanPackages || []
        const cleanStage = details.cleanStage || null
        const damagedPackages = details.damagedPackages || order.damaged_items || []
        const damagedStage = details.damagedStage || (damagedPackages.length ? 'repair' : null)

        if (cleanPackages.length && cleanStage === 'wash') {
          entries.push(mapOrderToMaintenanceItem(order, 'wash', cleanPackages, 'clean'))
        }
        if (damagedPackages.length && damagedStage === 'wash') {
          entries.push(mapOrderToMaintenanceItem(order, 'wash', damagedPackages, 'damaged'))
        }

        return entries
      }),
    ],
    completedQueue: completedOrders
      .filter(order => order.damaged || order.damage_status > 0)
      .slice(0, 10)
      .map(order => mapOrderToMaintenanceItem(order, 'ready', detailsMap[order.orderID]?.allSelected || order.selected_items || [], 'all'))
  }
}
