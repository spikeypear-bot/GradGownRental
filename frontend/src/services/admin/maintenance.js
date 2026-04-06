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

function buildItemStageKey(item = {}) {
  if (item.damageId) {
    return `damage-${item.damageId}`
  }
  return [item.modelId, item.qty || 1, item.chosenDate || ''].join(':')
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

// Map individual items from packages into table rows with full details
export function mapPackagesToTableItems(packages = []) {
  return packages.flatMap(pkg => {
    if (Array.isArray(pkg)) {
      return pkg.map(item => ({
        queueKey: buildItemStageKey(item),
        modelId: item.modelId,
        damageId: item.damageId ?? null,
        itemName: item.itemName || 'Unknown Item',
        itemType: item.itemType || 'unknown',
        size: item.size || 'Unknown Size',
        qty: item.qty || 1,
        selectedPackages: [item]
      }))
    }
    return [{
      queueKey: buildItemStageKey(pkg),
      modelId: pkg.modelId,
      damageId: pkg.damageId ?? null,
      itemName: pkg.itemName || 'Unknown Item',
      itemType: pkg.itemType || 'unknown',
      size: pkg.size || 'Unknown Size',
      qty: pkg.qty || 1,
      selectedPackages: [pkg]
    }]
  })
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
      const damagedItemStages = details.damagedItemStages || {}
      return mapPackagesToTableItems(damagedPackages)
        .filter(item => (damagedItemStages[item.queueKey] || 'repair') === 'repair')
        .map(item => ({
        ...item,
        orderId: order.orderID,
        subsetKey: 'damaged'
        }))
    }),
    washQueue: [
      ...damagedOrders.flatMap(order => {
        const details = detailsMap[order.orderID] || {}
        const entries = []
        const cleanPackages = details.cleanPackages || []
        const cleanItemStages = details.cleanItemStages || {}
        const damagedPackages = details.damagedPackages || order.damaged_items || []
        const damagedItemStages = details.damagedItemStages || {}

        if (damagedPackages.length) {
          entries.push(...mapPackagesToTableItems(damagedPackages)
            .filter(item => damagedItemStages[item.queueKey] === 'wash')
            .map(item => ({
            ...item,
            orderId: order.orderID,
            subsetKey: 'damaged'
          })))
        }

        if (cleanPackages.length) {
          entries.push(...mapPackagesToTableItems(cleanPackages)
            .filter(item => (cleanItemStages[item.queueKey] || 'wash') === 'wash')
            .map(item => ({
            ...item,
            orderId: order.orderID,
            subsetKey: 'clean'
          })))
        }

        return entries
      }),
      ...returnedOrders.flatMap(order => {
        const details = detailsMap[order.orderID] || {}
        const cleanPackages = details.cleanPackages || details.allSelected || order.selected_items || []
        const cleanItemStages = details.cleanItemStages || {}
        return mapPackagesToTableItems(cleanPackages)
          .filter(item => (cleanItemStages[item.queueKey] || 'wash') === 'wash')
          .map(item => ({
          ...item,
          orderId: order.orderID,
          subsetKey: 'clean'
          }))
      }),
    ],
    completedQueue: completedOrders
      .filter(order => order.damaged || order.damage_status > 0)
      .slice(0, 10)
      .map(order => mapOrderToMaintenanceItem(order, 'ready', detailsMap[order.orderID]?.allSelected || order.selected_items || [], 'all'))
  }
}
